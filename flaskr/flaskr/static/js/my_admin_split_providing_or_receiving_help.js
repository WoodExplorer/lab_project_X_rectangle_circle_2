var admin_split_providing_or_receiving_help = function (target_url, entry_id, jb) {
        var corresponding_input_id = 'input_' + entry_id;
        var split_detail = $('#' + corresponding_input_id).val();
            
        var pieces = split_detail.split(",");      
        for (var i=0; i<pieces.length ; i++)   
        {   
            if (isNaN(pieces[i])) {
                alert("请输入合法数字，并用英文逗号分隔。");
                return;
            }
        }  
        pieces = pieces.map(function (x) { return Number(x); });
        var sum_of_pieces = pieces.reduce(function(acc,x){ return x+acc; });
        if (sum_of_pieces != jb) {
            alert("拆分后的分订单的金额总额与原订单不同。");
            return;
        }
        
        $.post(
            target_url,
            { entry_id: entry_id, 'pieces': pieces.join(',') },     
            function (jsonObj, textStatus){        
                console.log(jsonObj);   
                location.reload();
            }, 
            "json"
        );
    }