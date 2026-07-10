class Roll < Formula
  include Language::Python::Virtualenv

  desc "Personal film roll index"
  homepage "https://github.com/katrinio/roll"
  url "https://github.com/katrinio/roll/archive/refs/tags/v0.7.0.tar.gz"
  sha256 "__REPLACE_WITH_RELEASE_SHA256__"
  license "MIT"

  depends_on "python@3.12"

  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.16.0.tar.gz"
    sha256 "__REPLACE_WITH_TYPER_SHA256__"
  end

  resource "prompt-toolkit" do
    url "https://files.pythonhosted.org/packages/source/p/prompt_toolkit/prompt_toolkit-3.0.51.tar.gz"
    sha256 "__REPLACE_WITH_PROMPT_TOOLKIT_SHA256__"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    archive = testpath/"archive"
    system bin/"rl", "init", archive
    assert_predicate archive/".roll", :directory?
    assert_predicate archive/".roll"/"stock.toml", :exist?
  end
end
