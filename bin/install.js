#!/usr/bin/env node

/**
 * link-article-writer 安装脚本
 *
 * 功能：
 * 1. 将技能安装到 ~/.agents/skills/link-article-writer
 * 2. 在 ~/.claude/skills/ 创建符号链接
 *
 * 使用方式：
 * - npx link-article-writer          # 一次性安装
 * - npm install -g link-article-writer  # 全局安装
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// 跨平台获取用户主目录
function getHomeDir() {
  return os.homedir();
}

// 路径配置
const SKILL_NAME = 'link-article-writer';
const HOME_DIR = getHomeDir();
const AGENTS_SKILLS_DIR = path.join(HOME_DIR, '.agents', 'skills');
const CLAUDE_SKILLS_DIR = path.join(HOME_DIR, '.claude', 'skills');
const TARGET_DIR = path.join(AGENTS_SKILLS_DIR, SKILL_NAME);

// 获取技能源目录（脚本所在位置）
function getSourceDir() {
  // 当通过 npx 运行时，__dirname 是临时缓存目录
  // 当从已安装目录运行时，需要找到正确的源位置
  return path.resolve(__dirname, '..');
}

// 创建符号链接（跨平台）
function createSymlink(target, linkPath) {
  // Windows 上需要管理员权限才能创建符号链接
  // 使用 junction 作为替代方案（目录链接，不需要特殊权限）
  const isWindows = process.platform === 'win32';

  try {
    // 确保父目录存在
    const parentDir = path.dirname(linkPath);
    if (!fs.existsSync(parentDir)) {
      fs.mkdirSync(parentDir, { recursive: true });
    }

    // 如果已存在链接或目录，先移除
    if (fs.existsSync(linkPath)) {
      const stats = fs.lstatSync(linkPath);
      if (stats.isSymbolicLink() || stats.isDirectory()) {
        fs.rmSync(linkPath, { recursive: true });
      }
    }

    if (isWindows) {
      // Windows: 使用 junction（不需要管理员权限）
      // mklink /J 创建目录联接
      const result = execSync(`cmd /c mklink /J "${linkPath}" "${target}"`, { stdio: 'pipe' });
      console.log(`  Created junction: ${linkPath} -> ${target}`);
    } else {
      // Unix: 使用符号链接
      fs.symlinkSync(target, linkPath, 'dir');
      console.log(`  Created symlink: ${linkPath} -> ${target}`);
    }
    return true;
  } catch (error) {
    console.error(`  Failed to create link at ${linkPath}: ${error.message}`);
    return false;
  }
}

// 简单的 execSync 实现
const { execSync } = require('child_process');
function execSync(command, options = {}) {
  return require('child_process').execSync(command, { stdio: 'pipe', ...options });
}

// 复制目录内容
function copyDir(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// 主安装函数
function install() {
  console.log('\n🔧 link-article-writer 安装程序\n');

  const sourceDir = getSourceDir();
  console.log(`📦 源目录: ${sourceDir}`);

  // 检查源目录是否存在
  if (!fs.existsSync(sourceDir)) {
    console.error(`❌ 错误: 源目录不存在: ${sourceDir}`);
    process.exit(1);
  }

  // 检查 SKILL.md 是否存在
  const skillMdPath = path.join(sourceDir, 'SKILL.md');
  if (!fs.existsSync(skillMdPath)) {
    console.error(`❌ 错误: SKILL.md 不存在于源目录`);
    process.exit(1);
  }

  // Step 1: 确保目标父目录存在
  console.log('\n📁 创建目录结构...');
  if (!fs.existsSync(AGENTS_SKILLS_DIR)) {
    fs.mkdirSync(AGENTS_SKILLS_DIR, { recursive: true });
    console.log(`  Created: ${AGENTS_SKILLS_DIR}`);
  }

  if (!fs.existsSync(CLAUDE_SKILLS_DIR)) {
    fs.mkdirSync(CLAUDE_SKILLS_DIR, { recursive: true });
    console.log(`  Created: ${CLAUDE_SKILLS_DIR}`);
  }

  // Step 2: 复制或更新技能目录
  console.log('\n📦 安装技能到 ~/.agents/skills/...');

  // 检查是否是从已安装目录运行（避免重复复制）
  const isAlreadyInstalled = path.resolve(sourceDir) === path.resolve(TARGET_DIR);

  if (isAlreadyInstalled) {
    console.log('  ✓ 技能已在正确位置');
  } else {
    // 复制到目标位置
    if (fs.existsSync(TARGET_DIR)) {
      console.log('  🗑️  移除旧版本...');
      fs.rmSync(TARGET_DIR, { recursive: true });
    }
    copyDir(sourceDir, TARGET_DIR);
    console.log(`  ✓ 已复制到: ${TARGET_DIR}`);
  }

  // Step 3: 创建 Claude Skills 符号链接
  console.log('\n🔗 创建 ~/.claude/skills/ 符号链接...');
  const linkPath = path.join(CLAUDE_SKILLS_DIR, SKILL_NAME);

  const linkCreated = createSymlink(TARGET_DIR, linkPath);

  if (!linkCreated) {
    console.warn('\n⚠️  警告: 无法创建符号链接，可能需要手动操作');
    console.warn(`   请手动运行: mklink /J "${linkPath}" "${TARGET_DIR}"`);
  }

  // Step 4: 验证安装
  console.log('\n✅ 安装完成!\n');
  console.log('技能文件位置:');
  console.log(`  - ${TARGET_DIR}`);
  console.log(`  - ${linkPath}\n`);

  console.log('使用方式:');
  console.log('  在 Claude Code 中输入: /link-article-writer\n');
}

// 运行安装
install();
