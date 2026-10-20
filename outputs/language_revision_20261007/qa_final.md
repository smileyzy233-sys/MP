# 全文语言修订验收

权威来源为本轮读取的当前Word，SHA256为763f2f27c14d1bdb52d60c536bdc9693bcf8a0fe13a80025e9fe9aae58a9dae3，已与上次制作版本不同；旧Markdown和旧manifest未用于重建。

修改55段正文、39个表格单元和1条参考资料说明。polish_first_half与polish_second_half按nature-polishing分段润色，主代理检查全文、修订表格并复核表达。没有更改研究方法、标题、章节、数值或公式。

87个原生数学对象的规范化XML逐项完全一致。段落属性、表格属性、行列结构、章节页面设置一致；17个非正文OOXML成员字节一致。数字标记及公式字段保护标记保持不变。原件SHA256未变；Word只读渲染后输出SHA256未变。

Word修订版14页。luna_revision_visual检查1至7页，主代理检查8至14页；没有乱码、缺字或裁切。表格自然跨页且重复表头。仅交付DOCX，没有重建已删除的Markdown或新增对照报告。图像和PDF为临时验收材料，完成后清理。

采用nature-polishing、docx和documents:documents的语言、结构保护及视觉验收方法。运行使用Codex捆绑Python及Poppler，Windows下用隔离Word实例只读导出，不安装新依赖、不使用用户LibreOffice。
