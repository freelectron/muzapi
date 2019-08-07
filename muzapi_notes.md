# Notes for muzapi project:

## MySQL:

### Sign Up

  - Used to store info about users and songs, and stuff.

  Steps to make it work:

  1) Install MySQL on the 'server'. Set up a user 'mapi' and give it all the permissions.

     **  MySQL's user name and password to login: mapi and mapi
     ** To log in:

```
mysql -u mapi -p
```

  2) Create a table with users' credentials.

```
CREATE DATABASE Muzapi;

CREATE TABLE `Muzapi`.`tbl_user` (
`user_id` BIGINT NOT NULL AUTO_INCREMENT,
`user_name` VARCHAR(45) NULL,
`user_username` VARCHAR(45) NULL,
`user_password` VARCHAR(512) NULL,
PRIMARY KEY (`user_id`));
````

   3) If you have an SQL query that you write over and over again, save it as a stored procedure, and then just call it to execute it.

      We will have to check whether user exists and create it if it doesnt exist.

	** Code of the 'stored procedure'

```
USE Muzapi;
DELIMITER $$
CREATE DEFINER=`mapi`@`localhost` PROCEDURE `sp_createUser`(
    IN p_name VARCHAR(45),
    IN p_username VARCHAR(45),
    IN p_password VARCHAR(512)
)
BEGIN
    if ( select exists (select 1 from tbl_user where user_username = p_username) ) THEN

	select 'Username Exists !!';

    ELSE

	insert into tbl_user
	(
	    user_name,
	    user_username,
	    user_password
	)
	values
	(
	    p_name,
	    p_username,
	    p_password
	);

    END IF ;
END$$
DELIMITER ;
```
  ** code explanation: we need the DELIMITER for SQL syntex. We want SQL to to see the whole code as one 'function' to execute on the call.
     And not just the first part which end with ; (semi-column)

   4) Call the MySQL Stored Procedure once we have the user credentials in the `signUp` method.


### Sign In

  1) Create a stored procedure to retrieve and check the credentials

```
DELIMITER $$
CREATE PROCEDURE `sp_validateLogin`(
IN p_username VARCHAR(20)
)
BEGIN
    select * from tbl_user where user_username = p_username;
END$$
DELIMITER ;
```


### Create a functionality to add a wish (later could be a song or film)

  1) Create a table in Muzapi, where the data is going to be stored

```
CREATE TABLE `tbl_wish` (
  `wish_id` int(11) NOT NULL AUTO_INCREMENT,
  `wish_title` varchar(45) DEFAULT NULL,
  `wish_description` varchar(5000) DEFAULT NULL,
  `wish_user_id` int(11) DEFAULT NULL,
  `wish_date` datetime DEFAULT NULL,
  PRIMARY KEY (`wish_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
```

  2) Create a stored procedure which will put entered data to the table.

  ** why if exists?

```
USE `Muzapi`;
DROP procedure IF EXISTS `Muzapi`.`sp_addWish`;

DELIMITER $$
USE `Muzapi`$$
CREATE PROCEDURE `sp_addWish`(
    IN p_title varchar(45),
    IN p_description varchar(1000),
    IN p_user_id bigint
)
BEGIN
    insert into tbl_wish(
        wish_title,
        wish_description,
        wish_user_id,
        wish_date
    )
    values
    (
        p_title,
        p_description,
        p_user_id,
        NOW()
    );
END$$

DELIMITER ;
;
```

  3) Display a List Item from tbl_wish.

  ** Stored procedure which will get the wishes created by a user. It will take the user
      ID as a parameter and return a data set of wishes created by the particular user ID

```
USE `Muzapi` ;
DROP procedure IF EXISTS `sp_GetWishByUser`;

DELIMITER $$
USE `Muzapi` $$
CREATE PROCEDURE `sp_GetWishByUser` ( IN p_user_id bigint )
BEGIN
  SELECT * FROM tbl_wish WHERE wish_user_id = p_user_id ;
END$$

DELIMITER ;
```

  4)
