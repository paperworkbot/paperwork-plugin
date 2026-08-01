#!/usr/bin/env ruby

require "fileutils"
require "minitest/autorun"
require "open3"
require "rbconfig"
require "tmpdir"

ROOT = File.expand_path("..", __dir__)
VALIDATOR = File.join(ROOT, "scripts/validate-plugin.rb")

class ValidatePluginTest < Minitest::Test
  def test_rejects_repository_reference_removed_from_current_tree
    with_clone do |repository|
      private_repository = ["private-owner", "private-repository"].join("/")
      readme = File.join(repository, "README.md")

      File.open(readme, "a") { |file| file.puts("\nInternal source: #{private_repository}") }
      git(repository, "add", "README.md")
      git(repository, "commit", "-m", "Add internal source reference")

      File.write(readme, File.read(readme).sub("\nInternal source: #{private_repository}\n", ""))
      git(repository, "add", "README.md")
      git(repository, "commit", "-m", "Remove internal source reference")

      _stdout, stderr, status = run_validator(repository)

      refute status.success?
      assert_match(
        /Git history(?: file \S+)? contains an unapproved repository shorthand/,
        stderr
      )
    end
  end

  def test_rejects_repository_reference_in_release_metadata
    private_repository = ["private-owner", "private-repository"].join("/")
    _stdout, stderr, status = run_validator(
      ROOT,
      "PAPERWORK_PUBLIC_METADATA" => "Depends on #{private_repository}"
    )

    refute status.success?
    assert_includes stderr, "public metadata contains an unapproved repository shorthand"
  end

  def test_rejects_repository_reference_in_branch_name
    with_clone do |repository|
      private_repository = ["private-owner", "private-repository"].join("/")
      git(repository, "branch", private_repository)

      _stdout, stderr, status = run_validator(repository)

      refute status.success?
      assert_match(
        /Git ref \S+ contains an unapproved repository shorthand/,
        stderr
      )
    end
  end

  private

  def with_clone
    Dir.mktmpdir("paperwork-plugin-validation") do |directory|
      repository = File.join(directory, "repository")
      FileUtils.mkdir_p(repository)
      Dir.children(ROOT).reject { |name| name == ".git" }.each do |name|
        FileUtils.cp_r(File.join(ROOT, name), repository)
      end
      git(repository, "init", "--quiet", "--initial-branch=main")
      git(repository, "config", "user.name", "Release Validation")
      git(repository, "config", "user.email", "release-validation@example.invalid")
      git(repository, "add", ".")
      git(repository, "commit", "-m", "Create clean distribution")
      yield repository
    end
  end

  def git(repository, *arguments)
    run!("git", "-C", repository, *arguments)
  end

  def run_validator(repository, environment = {})
    Open3.capture3(
      environment,
      RbConfig.ruby,
      File.join(repository, "scripts/validate-plugin.rb"),
      chdir: repository
    )
  end

  def run!(*command)
    _stdout, stderr, status = Open3.capture3(*command)
    raise "Command failed: #{command.join(" ")}\n#{stderr}" unless status.success?
  end
end
