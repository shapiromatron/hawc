# Health Assessment Workspace Collaborative

[![Documentation Status](https://readthedocs.org/projects/hawc/badge/)](https://hawc.readthedocs.io)

The Health Assessment Workspace Collaborative (HAWC) is a website designed to capture key data and analyses performed in conducting human-health assessment of chemicals and other environmental exposures in-order to establish hazard identification and potentially derive quantitative levels of concern.

## Yarn Installation

HAWC requires [Yarn](https://yarnpkg.com/) < 2 for JavaScript package management. Choose one of the following installation methods based on your operating system:

### Mac

Install via Homebrew:
```bash
brew install yarn
```

### Universal (npm/npx)

Install globally via npm:
```bash
npm install -g yarn
```

Or use npx to run Yarn without installing globally:
```bash
npx yarn --version
```

### Windows

1. **Download Windows Installer**: Visit [https://yarnpkg.com/getting-started/install](https://yarnpkg.com/getting-started/install) and download the Windows installer (.msi file)
2. **Run the installer**: Double-click the downloaded file and follow the installation wizard
3. **Verify installation**: Open a new command prompt and run `yarn --version`

Alternatively, you can use package managers like Chocolatey or Scoop:

```powershell
# Using Chocolatey
choco install yarn

# Using Scoop
scoop install yarn
```

**Note**: HAWC requires Yarn version < 2. You can check your version with `yarn --version` and ensure it starts with `1.`
