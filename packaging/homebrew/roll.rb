class Roll < Formula
  include Language::Python::Virtualenv

  desc "Personal film roll index"
  homepage "https://github.com/katrinio/roll"
  url "https://github.com/katrinio/roll/archive/refs/tags/v0.8.1.tar.gz"
  sha256 "__REPLACE_WITH_RELEASE_SHA256__"
  license "MIT"

  depends_on "python@3.12"

  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.16.0.tar.gz"
    sha256 "__REPLACE_WITH_TYPER_SHA256__"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/source/c/click/click-8.4.2.tar.gz"
    sha256 "9a6cea6e60b17ebe0a44c5cc636d94f09bd66142c1cd7d8b4cd731c4917a15f6"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-15.0.0.tar.gz"
    sha256 "edd07a4824c6b40189fb7ac9bc4c52536e9780fbbfbddf6f1e2502c31b068c36"
  end

  resource "shellingham" do
    url "https://files.pythonhosted.org/packages/source/s/shellingham/shellingham-1.5.4.tar.gz"
    sha256 "8dbca0739d487e5bd35ab3ca4b36e11c4078f3a234bfce294b0a0291363404de"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/source/m/markdown_it_py/markdown_it_py-4.2.0.tar.gz"
    sha256 "04a21681d6fbb623de53f6f364d352309d4094dd4194040a10fd51833e418d49"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/source/m/mdurl/mdurl-0.1.2.tar.gz"
    sha256 "bb413d29f5eea38f31dd4754dd7377d4465116fb207585f97bf925588687c1ba"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/source/p/pygments/pygments-2.20.0.tar.gz"
    sha256 "6757cd03768053ff99f3039c1a36d6c0aa0b263438fcab17520b30a303a82b5f"
  end

  resource "prompt-toolkit" do
    url "https://files.pythonhosted.org/packages/source/p/prompt_toolkit/prompt_toolkit-3.0.51.tar.gz"
    sha256 "__REPLACE_WITH_PROMPT_TOOLKIT_SHA256__"
  end

  resource "wcwidth" do
    url "https://files.pythonhosted.org/packages/source/w/wcwidth/wcwidth-0.8.2.tar.gz"
    sha256 "91fbef97204b96a3d4d421609b80340b760cf33e26da123ff243d76b1fda8dda"
  end

  def install
    # GitHub source archives do not reliably preserve enough VCS metadata for
    # setuptools-scm, so pin the package version from the formula itself.
    ENV["SETUPTOOLS_SCM_PRETEND_VERSION_FOR_ROLL"] = version.to_s
    virtualenv_install_with_resources
  end

  test do
    archive = testpath/"archive"
    archive.mkpath
    system bin/"rl", "init", archive
    assert_predicate archive/".roll", :directory?
    assert_predicate archive/".roll"/"stock.toml", :exist?
  end
end
