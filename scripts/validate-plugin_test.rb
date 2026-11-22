require "fileutils"
require "json"
require "minitest/autorun"
require "open3"
require "rbconfig"
require "tmpdir"

ROOT = File.expand_path("..", __dir__)

class ValidatePluginTest < Minitest::Test
  def test_rejects_a_stale_marketplace_or_capability_catalog_version
    [".claude-plugin/marketplace.json", "plugins/paperwork/skills/paperwork/references/capabilities.yml"].each do |relative|
      Dir.mktmpdir("paperwork-plugin-validation") do |directory|
        distribution = File.join(directory, "distribution")
        FileUtils.cp_r(ROOT, distribution)
        path = File.join(distribution, relative)
        version = JSON.parse(File.read(File.join(distribution, "plugins/paperwork/.codex-plugin/plugin.json"))).fetch("version")
        File.write(path, File.read(path).sub(version, "0.0.1"))

        _stdout, stderr, status = Open3.capture3(
          RbConfig.ruby, File.join(distribution, "scripts/validate-plugin.rb"), chdir: distribution
        )

        refute status.success?
        assert_includes stderr, "marketplace and capability catalog versions must match the manifests"
      end
    end
  end

  def test_ignores_git_administrative_file_in_a_linked_worktree
    Dir.mktmpdir("paperwork-plugin-validation") do |directory|
      distribution = File.join(directory, "distribution")
      FileUtils.mkdir_p(distribution)
      Dir.children(ROOT).reject { |name| name == ".git" }.each do |name|
        FileUtils.cp_r(File.join(ROOT, name), distribution)
      end

      worktree_path = ["", "Users", "example", "repository", ".git", "worktrees", "distribution"].join("/")
      File.write(File.join(distribution, ".git"), "gitdir: #{worktree_path}\n")

      _stdout, stderr, status = Open3.capture3(
        RbConfig.ruby,
        File.join(distribution, "scripts/validate-plugin.rb"),
        chdir: distribution
      )

      assert status.success?, stderr
    end
  end

  def test_rejects_more_than_three_codex_default_prompts
    Dir.mktmpdir("paperwork-plugin-validation") do |directory|
      distribution = File.join(directory, "distribution")
      FileUtils.cp_r(ROOT, distribution)
      manifest_path = File.join(distribution, "plugins/paperwork/.codex-plugin/plugin.json")
      manifest = JSON.parse(File.read(manifest_path))
      manifest.fetch("interface")["defaultPrompt"] = %w[one two three four]
      File.write(manifest_path, JSON.pretty_generate(manifest))

      _stdout, stderr, status = Open3.capture3(
        RbConfig.ruby,
        File.join(distribution, "scripts/validate-plugin.rb"),
        chdir: distribution
      )

      refute status.success?
      assert_includes stderr, "between one and three default prompts"
    end
  end

  def test_rejects_missing_current_version_in_changelog_or_inline_readme_changelog
    Dir.mktmpdir("paperwork-plugin-validation") do |directory|
      distribution = File.join(directory, "distribution")
      FileUtils.cp_r(ROOT, distribution)
      version = JSON.parse(File.read(File.join(distribution, "plugins/paperwork/.codex-plugin/plugin.json"))).fetch("version")
      changelog = File.join(distribution, "CHANGELOG.md")
      File.write(changelog, File.read(changelog).sub("## [#{version}]", "## [0.0.1]"))
      readme = File.join(distribution, "README.md")
      File.write(readme, "#{File.read(readme)}\nVersion #{version} adds inline notes.\n")

      _stdout, stderr, status = Open3.capture3(
        RbConfig.ruby,
        File.join(distribution, "scripts/validate-plugin.rb"),
        chdir: distribution
      )

      refute status.success?
      assert_includes stderr, "CHANGELOG.md must contain a ## [#{version}] section"
      assert_includes stderr, "README.md must link to CHANGELOG.md instead of carrying inline"
    end
  end
end
