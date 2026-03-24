CREATE TABLE `users` (
    `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(80) NOT NULL,
    `password` VARCHAR(80) NOT NULL,
    `privilege` INT NOT NULL DEFAULT 0,
    `disabled` BOOLEAN DEFAULT FALSE
);


CREATE TABLE `user_asset` (
    `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `userid` INT NOT NULL,
    `asset_name` VARCHAR(80) NOT NULL,
    CONSTRAINT `fk_user_asset_userid` FOREIGN KEY (`userid`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
);


CREATE TABLE `geofeed` (
    `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `userid` INT NOT NULL,
    `assetid` INT NOT NULL,
    `prefix` VARCHAR(80) NOT NULL,
    `country_code` VARCHAR(2) NOT NULL DEFAULT 'AQ',
    `region_code` VARCHAR(50) NULL,
    `city` VARCHAR(80) NULL,
    `postal_code` VARCHAR(80) NULL,
    CONSTRAINT `fk_geofeed_userid` FOREIGN KEY (`userid`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_geofeed_assetid` FOREIGN KEY (`assetid`) REFERENCES `user_asset`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
);