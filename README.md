# WuKong

wukong 是一个基于最新技术栈的管理系统模板，旨在提供高效、灵活、易扩展的开发体验。

## 主要特点

- **前沿技术栈**: 后端使用 FastAPI、Pydantic、Tortoise ORM，前端使用 Vue3、Vite5、TypeScript、Pinia 和 UnoCSS。
- **独特的访问控制**: 实现了前后端分离的用户角色和权限管理体系，针对不同角色实施严格权限控制。
- **详细的日志管理**: 基于 SoybeanAdmin，我们添加了日志管理和 API 访问控制功能，以满足实际业务需求并实现后端权限的深入验证。
- **集成实用工具**: 代码库中包含多个耦合度低的实用工具，部分工具经过优化和重写。
- **清晰的项目结构**: 使用 pnpm 和 monorepo 架构，项目结构简洁清晰，即使是大型项目也能快速上手。
- **严格的代码规范**: 前端遵循 SoybeanJS 规范，集成了 ESLint、Prettier 和 Simple Git Hooks；后端使用 Ruff 和 Pyright 进行静态分析和代码风格检查，确保代码质量。


## 使用方法

### 方法一：Docker Compose 部署

1. 克隆项目：

   ```bash
   git clone https://github.com/sleep1223/fast-soy-admin
   ```

2. 使用 Docker Compose 部署：

   ```bash
   sudo docker compose up -d
   ```

3. 查看日志：

   ```bash
   sudo docker compose logs -f
   ```

### 方法二：本地部署

1. 克隆项目：

   ```bash
   git clone https://github.com/sleep1223/fast-soy-admin
   ```

2. 安装依赖：

   ```bash
   pdm install
   cd web && pnpm i
   ```

3. 启动项目：

   - 前端：

     ```bash
     cd web && pnpm dev
     ```

   - 后端：

     ```bash
     pdm run run.py
     ```

## 贡献

我们欢迎所有形式的贡献。如果你有任何想法或建议，欢迎通过 Pull Request 或创建 Issue 与我们分享。

## 开源协议

本项目基于 MIT 协议开源，供学习和交流使用。商业使用请保留原作者的版权信息。