# 去除不必要的换行符工具

提供一个Python脚本，用于去除文本文件中不必要的换行符。它根据最常见的行长度范围和行尾标点符号，识别并合并可能属于同一句话的行。

### 功能特点

- 基于最常见的行长度范围移除不必要的换行符。
- 考虑行尾标点符号决定是否合并行。
- 可配置的行长度范围大小。
- 可配置的行尾标点符号正则表达式。

### 使用方法

1. 克隆或下载本项目到本地。

2. 运行脚本：

    ```bash
    python remove_line_breaks.py input_dir output_dir
    ```

建议calibre勾选智能处理后转换为epub，以优化排版。
