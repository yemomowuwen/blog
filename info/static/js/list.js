var currentCid = 1; // 当前分类 id==1 表示请求最新的数据
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   //true: 数据正在加载 false：没有人在加载数据


$(function () {
    Articles_list()

    $('.pagenation .n1').click(function(){
    cur_page += 1
    Articles_list()
    })

    $('.pagenation .n2').click(function(){
        cur_page -= 1
        Articles_list()
    })
})

function Articles_list() {
    var params = {
        'page': cur_page,
        'per_page': 14
    }
    $.get('/articles_list', params, function (resp) {
        if (resp){
            for (var i=0; i<resp.articles_List.length;i++){
                    var articles = resp.articles_List[i]
                    var content = '<li>'
                    content += '<span class="blogpic"><a href="/info/'+articles.id+'"><img src="'+articles.index_image_url+ '"></a></span>'
                    content += '<h3 class="blogtitle"><a href="/info/'+articles.id+'">'+articles.title+'</a></h3>'
                    content += '<div class="bloginfo"><p>'+articles.digest+'</p> </div>'
                    content += '<div class="autor"><span class="lm"><a href="/" title="'+articles.tag+'" target="_blank" class="classname">'+articles.tag+'</a></span><span class="dtime">'+articles.create_time+'</span><span class="viewnum">浏览(<a href="/">'+articles.clicks+'</a>)</span><span class="readmore"><a href="/info/'+articles.id+'">阅读原文</a></span></div>'
                    content += '</li>'
                   $('.blogs').append(content)
            }
            total_page = resp.total_Page
            cur_page = resp.current_Page
            var next_page = ''
            if(total_page==1){
            }
            else if(cur_page==1){
                next_page += '<div class="pagenation"><span class="n2">下一页&gt</span></div>'
            }
            else if(cur_page==total_page){
                next_page += '<div class="pagenation"><span class="n1">&lt上一页</span></div>'
            }
            else{
                next_page += '<div class="pagenation"><span class="n1">&lt上一页</span><span class="n2">下一页&gt</span></div>'
            }
            $('.blogs').append(next_page)
        }
    })
}

