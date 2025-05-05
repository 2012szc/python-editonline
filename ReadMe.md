# Python Online Editor

一个基于Flask的在线Python代码编辑器，支持代码运行、文件管理和终端功能。

## 功能特性

- **代码编辑**：支持Python语法高亮和自动补全
- **代码运行**：实时执行Python代码并显示输出结果
- **文件管理**：
  - 上传/下载Python文件
  - 保存/加载代码到服务器
  - 删除文件
- **终端功能**：内置命令行终端
- **主题切换**：支持多种编辑器主题

## 安装运行

1. 克隆仓库：
```bash
git clone https://github.com/your-repo/python-editonline.git
cd python-editonline
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

4. 访问应用：
```
http://localhost:5000/static/index.html
```

## API文档

### 文件操作API

- `POST /upload` - 上传文件
- `POST /save` - 保存文件
- `GET /load?filename=<filename>` - 加载文件
- `POST /delete_file` - 删除文件
- `GET /list_files` - 列出所有文件

### 代码执行API

- `POST /run_code` - 执行Python代码
- `POST /lint_code` - 代码静态检查
- `POST /autocomplete` - 代码自动补全

## 界面说明

- **左侧**：代码编辑器区域
- **右侧**：
  - 上部：代码运行结果
  - 下部：终端窗口
- **底部工具栏**：文件操作和功能按钮

## 注意事项

1. 请确保服务器有足够的权限执行Python代码
2. 文件操作会保存在服务器上的`edit`目录
3. 终端功能支持基本的Linux命令
