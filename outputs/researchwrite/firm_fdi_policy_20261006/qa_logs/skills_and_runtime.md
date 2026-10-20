# 技能与运行方式

researchwrite用于hybrid模式、事实与证据基础、论证图、章节契约及内容和语言审查。docx用于旧来源检查及Markdown中间稿。documents:documents用于python-docx、原生OMML、标题与表格规范、渲染视觉验收。agent-reach使用Exa核查PPML参考，另以官方网页确认文献信息。

依赖装载工具本轮未暴露，读取Codex桌面已部署runtime.json及对应本地包，采用26.921.10847捆绑Python 3.12.14及Node 24.19.0，未安装新依赖。Windows运行包没有LibreOffice；用隔离的Microsoft Word实例只读导出PDF，再用运行包Poppler转PNG。没有使用用户LibreOffice。Word实例在开始时必须没有其他文档，导出后关闭自己打开的只读文档，不保存DOCX。

公式由任务内支持本稿语法的TeX解析器生成MathML，使用本机Microsoft Office只读MML2OMML.XSL转换原生Word公式；没有栅格公式。数学测试检验求和下标、控制指示上下标、事件指示、效率变化、两行情景定义。修复单字母TeX词法后再全量构建。显示公式连续1至14；表A1至A5。

视觉迭代处理短表跨页、求和表达式作用域、行内大求和。根代理先完整检查13页，再复核最后版本7至13；luna_visual检查最后版本1至6。PNG及PDF为临时视觉中间件，验收后只保留文本指标、哈希与审查记录。
