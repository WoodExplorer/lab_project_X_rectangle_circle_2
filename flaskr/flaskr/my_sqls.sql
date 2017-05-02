alter table ot_user add column loginNum int default 0;

alter table ot_user add column last_sign_in datetime default NULL;

alter table ot_tgbz add column counted int default 0;


SET GLOBAL event_scheduler = ON;


CREATE EVENT e_update_static_purse
ON SCHEDULE EVERY 3600 SECOND
DO 
    call proc_e();
;