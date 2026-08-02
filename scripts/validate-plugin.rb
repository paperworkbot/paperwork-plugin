#!/usr/bin/env ruby

require "json"
require "pathname"
require "yaml"

ROOT = Pathname.new(File.expand_path("..", __dir__))
PLUGIN = ROOT.join("plugins/paperwork")
SKILLS = PLUGIN.join("skills")
errors = []

read_json = lambda do |path|
  JSON.parse(path.read)
rescue JSON::ParserError => error
  errors << "#{path.relative_path_from(ROOT)} is not valid JSON: #{error.message}"
  {}
end

read_yaml = lambda do |path|
  YAML.safe_load(path.read, permitted_classes: [], aliases: false) || {}
rescue Psych::Exception => error
  errors << "#{path.relative_path_from(ROOT)} is not valid YAML: #{error.message}"
  {}
end

claude_manifest_path = PLUGIN.join(".claude-plugin/plugin.json")
codex_manifest_path = PLUGIN.join(".codex-plugin/plugin.json")
marketplace_path = ROOT.join(".claude-plugin/marketplace.json")
mcp_path = PLUGIN.join(".mcp.json")
opencode_v1_path = ROOT.join("opencode.example.jsonc")
opencode_v2_path = ROOT.join("opencode-v2.example.jsonc")
capability_map_path = SKILLS.join("paperwork/references/capabilities.yml")

required_files = [
  claude_manifest_path,
  codex_manifest_path,
  marketplace_path,
  mcp_path,
  opencode_v1_path,
  opencode_v2_path,
  capability_map_path,
  ROOT.join("scripts/install-opencode.sh")
]
required_files.each do |path|
  errors << "missing #{path.relative_path_from(ROOT)}" unless path.file?
end

claude_manifest = read_json.call(claude_manifest_path)
codex_manifest = read_json.call(codex_manifest_path)
marketplace = read_json.call(marketplace_path)
mcp = read_json.call(mcp_path)
opencode_v1 = read_json.call(opencode_v1_path)
opencode_v2 = read_json.call(opencode_v2_path)
capability_map = read_yaml.call(capability_map_path)

errors << "Claude manifest name must be paperwork" unless claude_manifest["name"] == "paperwork"
errors << "Codex manifest name must be paperwork" unless codex_manifest["name"] == "paperwork"
unless claude_manifest["version"] == codex_manifest["version"]
  errors << "Claude and Codex manifest versions differ"
end
unless claude_manifest["version"].to_s.match?(/\A\d+\.\d+\.\d+\z/)
  errors << "manifest version must be a stable semantic version"
end
unless marketplace.dig("plugins", 0, "source") == "./plugins/paperwork"
  errors << "marketplace must point at ./plugins/paperwork"
end
unless codex_manifest["skills"] == "./skills/"
  errors << "Codex manifest must use the shared ./skills/ tree"
end

brand_asset = "./assets/paperwork-icon.svg"
unless codex_manifest.dig("interface", "brandColor") == "#EA473C"
  errors << "Codex manifest must declare the Paperwork brand color"
end
%w[composerIcon logo logoDark].each do |field|
  unless codex_manifest.dig("interface", field) == brand_asset
    errors << "Codex manifest #{field} must point at #{brand_asset}"
  end
end
errors << "missing #{brand_asset}" unless PLUGIN.join(brand_asset.delete_prefix("./")).file?

claude_server = mcp.dig("mcpServers", "paperwork") || {}
unless claude_server["url"] == "https://paperwork.bot/mcp"
  errors << "managed-cloud MCP URL must use the Paperwork HTTPS endpoint"
end
unless claude_server["oauth_resource"] == "https://paperwork.bot/mcp"
  errors << "managed-cloud MCP server must declare its OAuth resource"
end
if claude_server.key?("headers")
  errors << "managed-cloud MCP server must not require a bearer-token environment variable"
end

opencode_v1_server = opencode_v1.dig("mcp", "paperwork") || {}
unless opencode_v1_server["type"] == "remote"
  errors << "OpenCode v1 example must configure a remote MCP server"
end
unless opencode_v1_server.dig("headers", "Authorization") == "Bearer {env:PAPERWORK_MCP_TOKEN}"
  errors << "OpenCode v1 authorization must reference PAPERWORK_MCP_TOKEN"
end

opencode_v2_server = opencode_v2.dig("mcp", "servers", "paperwork") || {}
unless opencode_v2_server["type"] == "remote"
  errors << "OpenCode v2 example must configure a remote MCP server under mcp.servers"
end
unless opencode_v2_server.dig("headers", "Authorization") == "Bearer {env:PAPERWORK_MCP_TOKEN}"
  errors << "OpenCode v2 authorization must reference PAPERWORK_MCP_TOKEN"
end

skill_paths = SKILLS.children.select { |path| path.directory? && path.join("SKILL.md").file? }
skill_names = skill_paths.map { |path| path.basename.to_s }.sort
errors << "no skills found" if skill_names.empty?

skill_paths.each do |skill_path|
  relative = skill_path.relative_path_from(ROOT)
  contents = skill_path.join("SKILL.md").read
  match = contents.match(/\A---\n(.*?)\n---\n/m)
  unless match
    errors << "#{relative}/SKILL.md has no YAML frontmatter"
    next
  end

  metadata = YAML.safe_load(match[1], permitted_classes: [], aliases: false) || {}
  expected_name = skill_path.basename.to_s
  errors << "#{relative} declares the wrong skill name" unless metadata["name"] == expected_name
  errors << "#{relative} has no description" if metadata["description"].to_s.strip.empty?
  errors << "#{relative} is missing agents/openai.yaml" unless skill_path.join("agents/openai.yaml").file?

  contents.scan(/\]\(([^)]+)\)/).flatten.each do |link|
    next if link.start_with?("http://", "https://", "#")

    target = skill_path.join(link).cleanpath
    errors << "#{relative}/SKILL.md has a broken link: #{link}" unless target.exist?
  end
rescue Psych::Exception => error
  errors << "#{relative}/SKILL.md has invalid frontmatter: #{error.message}"
end

capabilities = capability_map.fetch("capabilities", {})
# The exact capability set is asserted against the live registry by
# spec/plugin/paperwork_plugin_spec.rb. This script runs standalone in the
# distribution repository, where the registry is unavailable, so it checks
# internal consistency instead of a hardcoded count that silently drifts.
errors << "no capabilities mapped" if capabilities.empty?
capabilities.each do |capability_name, mapping|
  Array(mapping && mapping["skills"]).each do |skill_name|
    next if skill_names.include?(skill_name)

    errors << "#{capability_name} references missing skill #{skill_name}"
  end
end
dynamic_tools = capability_map.fetch("dynamic_tools", {})
direct_custom_tasks = dynamic_tools.fetch("direct_custom_tasks", {})
unless direct_custom_tasks["mcp_pattern"] == "custom_task_*"
  errors << "direct custom tasks must use the custom_task_* MCP namespace"
end
unless direct_custom_tasks["run_status_mcp"] == "custom_task_runs_get"
  errors << "direct custom tasks must map custom_task_runs_get"
end
unless direct_custom_tasks["mode"] == "write" && direct_custom_tasks["scope"] == "workflow"
  errors << "direct custom tasks must be workflow-scoped writes"
end
Array(direct_custom_tasks["skills"]).each do |skill_name|
  errors << "direct custom tasks reference missing skill #{skill_name}" unless skill_names.include?(skill_name)
end

wire_names = []
capabilities.each do |name, entry|
  wire_name = entry["mcp"]
  wire_names << wire_name
  errors << "#{name} has the wrong MCP wire name" unless wire_name == name.tr(".", "_")
  errors << "#{name} mode must be read or write" unless %w[read write].include?(entry["mode"])
  errors << "#{name} scope must be account or workflow" unless %w[account workflow].include?(entry["scope"])

  mapped_skills = Array(entry["skills"])
  errors << "#{name} has no owning skill" if mapped_skills.empty?
  mapped_skills.each do |skill_name|
    errors << "#{name} references missing skill #{skill_name}" unless skill_names.include?(skill_name)
  end
end
errors << "capability MCP wire names are not unique" unless wire_names.uniq.length == wire_names.length

eval_paths = PLUGIN.join("evals").children.select(&:directory?)
errors << "expected at least six behavioral eval cases" unless eval_paths.length >= 6
eval_paths.each do |eval_path|
  errors << "#{eval_path.relative_path_from(ROOT)} is missing prompt.md" unless eval_path.join("prompt.md").file?
  graders = eval_path.join("graders")
  unless graders.directory? && graders.children.any? { |path| path.extname == ".md" }
    errors << "#{eval_path.relative_path_from(ROOT)} has no Markdown grader"
  end
end

allowed_executables = ["scripts/install-opencode.sh", "scripts/validate-plugin.rb"]
unfinished_pattern = Regexp.new(
  "\\[(?:TO" + "DO|FIX" + "ME):|(?<![A-Z])FIX" + "ME(?![A-Z])"
)
private_key_markers = %w[OPENSSH RSA EC].map do |kind|
  ["BEGIN", kind, "PRIVATE", "KEY"].join(" ")
end
public_boundary_patterns = {
  "a cross-repository issue or pull-request reference" =>
    /(?<![A-Za-z0-9_.-])[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+#\d+\b/,
  "a non-distribution GitHub repository URL" =>
    %r{https?://github\.com/(?!paperworkbot/paperwork-plugin\b)[^\s)"]+},
  "a local workstation or worktree path" =>
    Regexp.union(
      ["/", "Users", "/"].join,
      ["/", "home", "/"].join,
      ["C:", "\\", "Users", "\\"].join,
      [".claude", "worktrees", ""].join("/")
    )
}.freeze

scan_public_boundary = lambda do |label, contents|
  public_boundary_patterns.each do |description, pattern|
    errors << "#{label} contains #{description}" if contents.match?(pattern)
  end
end

ROOT.find do |path|
  next unless path.file?

  relative = path.relative_path_from(ROOT).to_s
  next if relative.start_with?(".git/")

  if path.executable? && !allowed_executables.include?(relative)
    errors << "unexpected executable component: #{relative}"
  end

  contents = path.binread
  next unless contents.valid_encoding?

  errors << "#{relative} contains an unfinished marker" if contents.match?(unfinished_pattern)
  errors << "#{relative} appears to contain a Paperwork token" if contents.match?(/pwcap_[A-Za-z0-9_-]{12,}/)
  errors << "#{relative} appears to contain a private key" if private_key_markers.any? { |marker| contents.include?(marker) }
  scan_public_boundary.call(relative, contents)
end

release_notes = ENV.fetch("PAPERWORK_RELEASE_NOTES", "")
scan_public_boundary.call("release notes", release_notes) unless release_notes.empty?

if errors.any?
  warn "PaperworkBot plugin validation failed:"
  errors.each { |error| warn "  - #{error}" }
  exit 1
end

puts "PaperworkBot plugin #{claude_manifest["version"]} is valid: " \
  "#{skill_names.length} skills, #{capabilities.length} fixed capabilities, " \
  "#{dynamic_tools.length} dynamic tool family, #{eval_paths.length} eval cases."
