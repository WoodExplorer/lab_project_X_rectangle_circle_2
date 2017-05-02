-- 如何打开事件调度器： 
---或我们可以在配置my.cnf文件 中加上 event_scheduler = 1



CREATE TABLE aaa (timeline TIMESTAMP);

CREATE EVENT e_test_insert
ON SCHEDULE EVERY 1 SECOND
DO INSERT INTO aaa VALUES(CURRENT_TIMESTAMP);


-- I guess this piece of sql will not compile.
CREATE EVENT IFNOT EXISTS `Slave_Monitor`
ONSCHEDULE EVERY 5 SECOND
ONCOMPLETION PRESERVE
DO
CALL Slave_Monitor();





CREATE TABLE b (d int);
insert into b values (1);

DELIMITER //  
CREATE PROCEDURE proc_b()  
BEGIN 
UPDATE b set d = d + 1;  
END 
//  
DELIMITER ; 


CREATE EVENT e_test_update_b
ON SCHEDULE EVERY 1 SECOND
DO CALL proc_b();



select DATEDIFF ( '2000:01:31 23:59:59', '2000:01:01 00:00:00');


--

drop procedure proc_d;
DELIMITER //  
CREATE PROCEDURE proc_d()  
BEGIN 
	DECLARE s1 int;
	DECLARE v_count int;
	DECLARE v_borrow_id int;
	
	DECLARE c_borrow CURSOR FOR   
        SELECT id FROM ot_tgbz;  
		
	SELECT count(ID) INTO v_count from ot_tgbz;
	
	SET s1 = 1;
	-- 开始事务
	START TRANSACTION;
	-- 打开游标
	OPEN c_borrow;
	-- 循环游标
	WHILE s1 < v_count+1 DO
		FETCH c_borrow INTO v_borrow_id;
		SELECT v_borrow_id;
		SET s1 = s1 + 1;
	END WHILE;
	CLOSE c_borrow;
 
	COMMIT; -- 事务提交 
 
END 
//  
DELIMITER; 
 

 
 -----------------------------------
 
 
drop procedure update_static_purse;
DELIMITER //  
CREATE PROCEDURE update_static_purse()  
BEGIN 
	DECLARE s1 int;
	DECLARE v_count int;
	DECLARE v_id int;
	DECLARE v_jb int;
	DECLARE v_date datetime;
	DECLARE v_now datetime;
	DECLARE v_zffs1 int;
	DECLARE v_zffs2 int;
	DECLARE v_user varchar(256);
	 
	DECLARE c_borrow CURSOR FOR 
		SELECT id, jb, date, zffs1, zffs2, user FROM ot_tgbz where counted=0 and zt=1 and qr_zt=1;  
		
	SELECT count(ID) INTO v_count from ot_tgbz;
	SELECT now() INTO v_now;
	
	SET s1 = 1;
	-- 开始事务
	START TRANSACTION;
	-- 打开游标
	OPEN c_borrow;
	-- 循环游标
	WHILE s1 < v_count+1 DO
		FETCH c_borrow INTO v_id, v_jb, v_date, v_zffs1, v_zffs2, v_user;
		
		IF 1 = v_zffs1 and datediff(v_now, v_date) >= 15 THEN
			update ot_tgbz set counted = 1 where id = v_id;
			update ot_user set ue_money = ue_money + v_jb * (1 + 0.12) + floor(v_jb / 1000) where UE_account = v_user;
			--update ot_user set ue_money = ue_money + v_jb where UE_account = v_user;
		END IF;
		
		IF 1 = v_zffs2 and datediff(v_now, v_date) >= 30 THEN
			update ot_tgbz set counted = 1 where id = v_id;
			update ot_user set ue_money = ue_money + v_jb * (1 + 0.40) + floor(v_jb / 1000)  where UE_account = v_user;
			--update ot_user set ue_money = ue_money + v_jb  where UE_account = v_user;
		END IF;
		
		SET s1 = s1 + 1;
	END WHILE;
	CLOSE c_borrow;
 
	COMMIT; -- 事务提交 
 
END 
//  
DELIMITER ; 
 
call update_static_purse();
 
 
