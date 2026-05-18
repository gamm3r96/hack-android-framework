# Contributing to hack-android-framework

Thank you for your interest in contributing to **hack-android-framework**! This project aims to make Android Open Source Project (AOSP) framework exploration, modification, and customization safe, educational, and well-documented. Whether you're fixing a bug, adding a new framework patch, improving documentation, or sharing a testing workflow, your contributions are highly valued.

---

## 📖 Getting Started

1. **Fork & Clone**
```bash
   git clone https://github.com/gamm3r96/hack-android-framework.git
   cd hack-android-framework
```

2. **Set Up Your Environment**
```bash
   chmod +x setup.sh && ./setup.sh
   # Follow AOSP build prerequisites in the main README if building from source
```

3. **Create a Feature Branch**
```bash
   git checkout -b feat/your-feature-name
```

---

## 🛠 Development Workflow

### 🔹 Code Structure
| Directory | Purpose |
|-----------|---------|
| `frameworks/base/` | Core Android framework (AMS, WMS, PMS, etc.) |
| `packages/SystemUI/` | Status bar, notifications, quick settings |
| `tools/` | Helper scripts for patching, building, and debugging |
| `docs/` | Architecture diagrams, guides, and reference material |
| `tests/` | Emulator configs, CTS snippets, and validation scripts |

### 🔹 Branch Naming Convention
- `feat/` for new features or framework modifications
- `fix/` for bug fixes or build issues
- `docs/` for documentation improvements
- `ci/` for workflow, script, or automation updates
- `refactor/` for code cleanup without functional changes

---

## 📝 Coding & Commit Standards

### ✅ Code Style
- **Java/Kotlin:** Follow [Android Code Style Guidelines](https://source.android.com/setup/contribute/code-style)
- **C/C++:** Use `clang-format` with the `.clang-format` config in the repo root
- **Shell/Python:** Follow `shellcheck` & `black`/`flake8` standards
- Run `./lint.sh` before committing to ensure formatting passes

### ✅ Commit Message Format
We follow a hybrid of **Conventional Commits** and **AOSP patch conventions**: