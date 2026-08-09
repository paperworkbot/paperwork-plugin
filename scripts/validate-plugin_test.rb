require "fileutils"
require "minitest/autorun"
require "open3"
require "rbconfig"
require "tmpdir"

ROOT = File.expand_path("..", __dir__)

class ValidatePluginTest < Minitest::Test
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
end
