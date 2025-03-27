# 文件分发系统

一个基于Web的文件分发系统，支持文件上传、MD5查询、文件列表查看、文件下载等功能，并提供完善的文件管理机制。

## 主要功能

- 文件上传：支持文件上传并自动计算MD5
- MD5查询：通过MD5值查询已上传的文件
- 文件查询：上传文件进行匹配查询
- 文件列表：查看所有已上传的文件
- 文件下载：支持文件在线下载
- 文件路径存储：保存文件的完整路径信息
- 相同MD5管理：支持同MD5不同文件名的文件管理
- 软删除：支持文件的软删除和恢复功能

## 技术栈

- 后端：Python + Flask
- 前端：HTML + CSS + JavaScript
- 数据库：SQLite

## 安装说明

1. 克隆项目到本地

```bash
git clone [项目地址]
cd file_distribution_system
```

2. 创建并激活虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 初始化数据库
启动应用的时候会自动初始化数据库，无需手动操作。
```python
...

db.init_app(app)
with app.app_context():
    db.create_all()

...
```

5. 运行应用

```bash
python app.py
```

访问 http://localhost:5000 即可使用系统。

## 接口说明

### 1. 文件上传接口 `/upload`
- 请求方法：POST
- 参数格式：
  - 使用multipart/form-data格式
  - 参数名：file
  - 参数类型：文件
- 示例命令：
  ```bash
  curl -X POST -F "file=@/path/to/your/file.txt" http://localhost:5000/upload
  ```
- 返回格式：
  ```json
  {
    "message": "File uploaded successfully",
    "md5": "文件的MD5值",
    "version": 文件版本号
  }
  ```

### 2. MD5查询接口 `/query/<md5>`
- 请求方法：GET
- 参数格式：
  - 在URL中直接传入MD5值
- 示例命令：
  ```bash
  curl http://localhost:5000/query/your_md5_here
  ```
- 返回格式：
  ```json
  {
    "md5": "文件的MD5值",
    "filenames": ["文件名1", "文件名2"],
    "file_path": "文件路径",
    "version": 文件版本号,
    "del_flag": false
  }
  ```

### 3. 文件查询接口 `/query_by_file`
- 请求方法：POST
- 参数格式：
  - 使用multipart/form-data格式
  - 参数名：file
  - 参数类型：文件
- 示例命令：
  ```bash
  curl -X POST -F "file=@/path/to/your/file.txt" http://localhost:5000/query_by_file
  ```
- 返回格式：
  ```json
  {
    "md5": "文件的MD5值",
    "filenames": ["文件名1", "文件名2"],
    "file_path": "文件路径",
    "version": 文件版本号,
    "del_flag": false
  }
  ```

### 4. 文件下载接口 `/download/<md5>/<filename>`
- 请求方法：GET
- 参数格式：
  - 在URL中传入MD5值和文件名
- 示例命令：
  ```bash
  curl -O http://localhost:5000/download/your_md5_here/filename.txt
  ```
- 返回格式：
  - 成功：直接返回文件内容
  - 失败：返回JSON格式错误信息
    ```json
    {
      "message": "错误信息"
    }
    ```

### 5. 文件列表接口 `/list`
- 请求方法：GET
- 参数格式：无需参数
- 示例命令：
  ```bash
  curl http://localhost:5000/list
  ```
- 返回格式：
  ```json
  [
    {
      "md5": "文件的MD5值",
      "filenames": ["文件名1", "文件名2"],
      "file_path": "文件路径",
      "version": 文件版本号,
      "del_flag": false
    },
    ...
  ]
  ```

## 使用说明

1. 文件上传
   - 点击"选择文件"按钮选择要上传的文件
   - 点击"上传文件"按钮完成上传
   - 系统会自动计算文件MD5并保存文件路径

2. MD5查询
   - 在输入框中输入MD5值
   - 点击"MD5查询"按钮查看结果
   - 支持查看同MD5下的所有文件名

3. 文件查询
   - 选择要查询的文件
   - 点击"文件查询"按钮进行匹配
   - 可查看文件的详细信息

4. 文件列表
   - 点击"文件列表"按钮查看所有文件
   - 支持文件下载功能
   - 可执行文件的软删除操作
   - 可恢复已软删除的文件

## 命令行调用

以下是使用curl命令进行接口调用的示例：

1. 文件上传
```bash
curl -X POST -F "file=@/path/to/your/file.txt" http://localhost:5000/upload
```

2. MD5查询
```bash
curl -X GET http://localhost:5000/query/your_md5_here
```

3. 文件查询
```bash
curl -X POST -F "file=@/path/to/your/file.txt" http://localhost:5000/query_by_file
```

4. 文件下载
```bash
curl -O http://localhost:5000/download/your_md5_here/filename.txt
```

5. 文件列表
```bash
curl http://localhost:5000/list
```

6. 删除文件
```bash
curl -X DELETE http://localhost:5000/delete/your_md5_here
```

## 注意事项

- 确保uploads目录具有写入权限
- 软删除的文件仍会保留在系统中，可随时恢复