CREATE TABLE `users` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(80) NOT NULL,
    `password` VARCHAR(80) NOT NULL,
    `privilege` INT NOT NULL DEFAULT 0,
    `disabled` BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_user_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `user_asset` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `userid` INT NOT NULL,
    `asset_name` VARCHAR(80) NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_user_asset_userid` (`userid`),
    CONSTRAINT `fk_user_asset_userid`
        FOREIGN KEY (`userid`) REFERENCES `user`(`id`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `geofeed` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `userid` INT NOT NULL,
    `assetid` INT NOT NULL,
    `prefix` VARCHAR(80) NOT NULL,
    `country_code` VARCHAR(2) NOT NULL DEFAULT 'AQ',
    `region_code` VARCHAR(50) NULL,
    `city` VARCHAR(80) NULL,
    `postal_code` VARCHAR(80) NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_geofeed_prefix` (`prefix`),
    KEY `idx_geofeed_userid` (`userid`),
    KEY `idx_geofeed_assetid` (`assetid`),
    CONSTRAINT `fk_geofeed_userid`
        FOREIGN KEY (`userid`) REFERENCES `user`(`id`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT `fk_geofeed_assetid`
        FOREIGN KEY (`assetid`) REFERENCES `user_asset`(`id`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;