


alter table ot_tgbz add column counted int default 0;

alter table ot_tgbz add column type int default 0;



update ot_user set UE_lastTime = null;


update ot_tgbz set counted=1;

update ot_user set UE_password = '0a8113941d35466c79218e83175665ef';



SET GLOBAL event_scheduler = ON;
SELECT @@event_scheduler;

注意，这里还是先创建那个存储过程再创建这个事件吧？主要是担心创建这个事件会马上触发这个事件……注意，最好在执行完前面那条对counted的更新语句后再创建update_static_purse存储过程和相应事件<==同样也是担心“创建那个事件会马上触发这个事件”…

CREATE EVENT e_update_static_purse
ON SCHEDULE EVERY 3600 SECOND
DO 
    call update_static_purse();
;





