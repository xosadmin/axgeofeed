CREATE TABLE `users` (
    `id` VARCHAR(80) PRIMARY KEY NOT NULL,
    `username` VARCHAR(80) NOT NULL,
    `password` VARCHAR(1000) NOT NULL,
    `privilege` INT NOT NULL DEFAULT 0,
    `disabled` BOOLEAN DEFAULT FALSE
);

INSERT INTO `users`(id,username,password,privilege,disabled)
VALUES ("00000000","admin","JDJiJDEyJFdmWFByTGpubHdPZUxTTTMyZ0hLUy42d0l6SHBscHpuTE5sd2tEVWtSMXg4enNxbEdXWlBH",
        0,0);
-- Create a default admin user with username and password combination of admin / admin.

CREATE TABLE `user_asset` (
    `id` VARCHAR(80) PRIMARY KEY NOT NULL,
    `userid` VARCHAR(80) NOT NULL,
    `asset_name` VARCHAR(80) NOT NULL,
    CONSTRAINT `fk_user_asset_userid` FOREIGN KEY (`userid`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
);

INSERT INTO `user_asset`(id,userid,asset_name)
VALUES("00000000","00000000","admin_MANUAL");
-- Add a default AS-SET for manual input from admin user

CREATE TABLE `geofeed` (
    `id` VARCHAR(80) PRIMARY KEY NOT NULL,
    `userid` VARCHAR(80) NOT NULL,
    `assetid` VARCHAR(80) NOT NULL,
    `prefix` VARCHAR(80) NOT NULL,
    `country_code` VARCHAR(2) NOT NULL DEFAULT 'AQ',
    `region_code` VARCHAR(50) NULL,
    `city` VARCHAR(80) NULL,
    `postal_code` VARCHAR(80) NULL,
    CONSTRAINT `fk_geofeed_userid` FOREIGN KEY (`userid`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_geofeed_assetid` FOREIGN KEY (`assetid`) REFERENCES `user_asset`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
);