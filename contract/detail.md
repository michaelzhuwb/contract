1. 登入页
    - 验证用户登入信息转入主页

2. 主页
    + 展示上传的合同列表
        + 具分页功能
            - 合同总数过多情况下分页展示
        + 具备模糊查询功能
            - 通过公司名称，劳动合同名称等。
        + 具备分类功能
            - 根据公司名称、上传合同时间展示合同列表
        - 显示的合同信息和相似度(未鉴伪为空)
    + 添加合同
        + 通过模态框处理，完成后主页进行合同列表局部刷新
            - 上传人
            - 上传时间
            - 劳动合同名称
            - 所属公司
            - 生成防伪码
        + 保存合同信息
            - 防伪码的加密后的信息设置为主键id，同时保存模态框填写的信息到sqlite
            - 将防伪码加入进合同，同时保存防伪合同pdf到本地
    + 鉴伪合同
        +  通过模态框添加最新合同图片，完成后转到合同对比页面
            - 引用第三方ocr识别出信息与防伪合同pdf信息对比得到相似度
            - 保存该合同相似度信息到sqlite表中  
    + 打印
        - 将防伪合同展示于网页,使用浏览器打印功能
    + 下载
        - 将防伪合同pdf下载

3. 合同对比页
    - 展示差异 还没有构思好