-- ============================================
-- 会场精灵 - 数据库设计
-- 版本: 1.0
-- 日期: 2026-03-30
-- ============================================

-- 使用 utf8mb4 字符集以支持 emoji
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 1. 主办方账户表 (organizers)
-- ============================================
DROP TABLE IF EXISTS `organizers`;
CREATE TABLE `organizers` (
    `id` INT UNSIGNED AUTO_INCREMENT COMMENT '主办方ID',
    `username` VARCHAR(50) NOT NULL COMMENT '登录用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希(BCrypt)',
    `organizer_name` VARCHAR(100) NOT NULL COMMENT '主办方名称',
    `contact_person` VARCHAR(50) DEFAULT NULL COMMENT '负责人姓名',
    `phone` VARCHAR(20) NOT NULL COMMENT '联系电话',
    `email` VARCHAR(100) NOT NULL COMMENT '联系邮箱',
    `address` VARCHAR(255) DEFAULT NULL COMMENT '主办方办公地址',
    `status` TINYINT UNSIGNED DEFAULT 1 COMMENT '状态: 0-禁用, 1-正常',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `last_login_at` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='主办方账户表';

-- ============================================
-- 2. 活动详情表 (activities)
-- ============================================
DROP TABLE IF EXISTS `activities`;
CREATE TABLE `activities` (
    `id` INT UNSIGNED AUTO_INCREMENT COMMENT '活动ID',
    `organizer_id` INT UNSIGNED NOT NULL COMMENT '主办方ID',
    `activity_name` VARCHAR(200) NOT NULL COMMENT '活动完整名称',
    `start_time` DATETIME NOT NULL COMMENT '开始时间',
    `end_time` DATETIME NOT NULL COMMENT '结束时间',
    `address` VARCHAR(255) NOT NULL COMMENT '活动详细地址',
    `description` TEXT COMMENT '活动简介',
    `requires_ticket` TINYINT(1) DEFAULT 0 COMMENT '是否需要购票: 0-否, 1-是',
    `ticket_url` VARCHAR(500) DEFAULT NULL COMMENT '购票链接',
    `ticket_price` VARCHAR(100) DEFAULT NULL COMMENT '票价信息',
    `ticket_deadline` DATETIME DEFAULT NULL COMMENT '购票截止时间',
    `status` TINYINT UNSIGNED DEFAULT 1 COMMENT '状态: 0-草稿, 1-已发布, 2-已结束, 3-已取消',
    `view_count` INT UNSIGNED DEFAULT 0 COMMENT '浏览次数',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_organizer_id` (`organizer_id`),
    KEY `idx_start_time` (`start_time`),
    KEY `idx_status` (`status`),
    KEY `idx_created_at` (`created_at`),
    FOREIGN KEY (`organizer_id`) REFERENCES `organizers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活动详情表';

-- ============================================
-- 3. 子活动详情表 (sub_activities)
-- ============================================
DROP TABLE IF EXISTS `sub_activities`;
CREATE TABLE `sub_activities` (
    `id` INT UNSIGNED AUTO_INCREMENT COMMENT '子活动ID',
    `activity_id` INT UNSIGNED NOT NULL COMMENT '所属主活动ID',
    `sub_name` VARCHAR(200) NOT NULL COMMENT '子活动名称',
    `start_time` DATETIME DEFAULT NULL COMMENT '开始时间',
    `end_time` DATETIME DEFAULT NULL COMMENT '结束时间',
    `location` VARCHAR(255) DEFAULT NULL COMMENT '地点',
    `description` TEXT COMMENT '简介',
    `sort_order` INT UNSIGNED DEFAULT 0 COMMENT '排序顺序',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_activity_id` (`activity_id`),
    KEY `idx_start_time` (`start_time`),
    KEY `idx_sort_order` (`sort_order`),
    FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='子活动详情表';

-- ============================================
-- 4. 活动标签表 (activity_tags)
-- ============================================
DROP TABLE IF EXISTS `activity_tags`;
CREATE TABLE `activity_tags` (
    `id` INT UNSIGNED AUTO_INCREMENT COMMENT '标签ID',
    `activity_id` INT UNSIGNED NOT NULL COMMENT '活动ID',
    `tag_name` VARCHAR(50) NOT NULL COMMENT '标签名称',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_activity_tag` (`activity_id`, `tag_name`),
    KEY `idx_tag_name` (`tag_name`),
    FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活动标签表';

-- ============================================
-- 5. 匿名对话记录表 (chat_logs)
-- ============================================
DROP TABLE IF EXISTS `chat_logs`;
CREATE TABLE `chat_logs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT COMMENT '对话ID',
    `session_id` VARCHAR(64) NOT NULL COMMENT '匿名会话标识(UUID)',
    `activity_id` INT UNSIGNED DEFAULT NULL COMMENT '关联的活动ID(可选)',
    `user_message` TEXT NOT NULL COMMENT '用户提问',
    `assistant_response` TEXT COMMENT '助手回答',
    `response_time_ms` INT UNSIGNED DEFAULT NULL COMMENT '响应耗时(毫秒)',
    `ip_address` VARCHAR(45) DEFAULT NULL COMMENT '用户IP地址',
    `user_agent` VARCHAR(500) DEFAULT NULL COMMENT '用户浏览器信息',
    `is_helpful` TINYINT(1) DEFAULT NULL COMMENT '是否有帮助: 0-否, 1-是, NULL-未评价',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_session_id` (`session_id`),
    KEY `idx_activity_id` (`activity_id`),
    KEY `idx_created_at` (`created_at`),
    FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='匿名对话记录表';

-- ============================================
-- 6. 活动附件表 (activity_attachments) - 可选扩展
-- ============================================
DROP TABLE IF EXISTS `activity_attachments`;
CREATE TABLE `activity_attachments` (
    `id` INT UNSIGNED AUTO_INCREMENT COMMENT '附件ID',
    `activity_id` INT UNSIGNED NOT NULL COMMENT '活动ID',
    `file_name` VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `file_path` VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    `file_size` INT UNSIGNED NOT NULL COMMENT '文件大小(字节)',
    `file_type` VARCHAR(100) NOT NULL COMMENT '文件MIME类型',
    `uploaded_by` INT UNSIGNED NOT NULL COMMENT '上传者ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    PRIMARY KEY (`id`),
    KEY `idx_activity_id` (`activity_id`),
    FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`uploaded_by`) REFERENCES `organizers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活动附件表';

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 初始化数据
-- ============================================

-- 插入测试主办方账号 (密码: 123456)
-- 注意: 生产环境请使用 BCrypt 加密密码
INSERT INTO `organizers` (`username`, `password_hash`, `organizer_name`, `contact_person`, `phone`, `email`, `address`, `status`) VALUES
('master', '$2a$10$YourHashedPasswordHere', '测试主办方', '管理员', '13800138000', 'admin@example.com', '上海市浦东新区测试地址', 1);

-- 插入示例活动数据
INSERT INTO `activities` (`organizer_id`, `activity_name`, `start_time`, `end_time`, `address`, `description`, `requires_ticket`, `ticket_url`, `ticket_price`, `ticket_deadline`, `status`) VALUES
(1, '国际创新博览会 2026', '2026-03-20 09:00:00', '2026-03-22 18:00:00', '上海国际会展中心 - 上海市浦东新区龙阳路2345号', '汇聚全球创新科技，展示最新科技成果', 1, 'https://tickets.example.com/expo2026', '早鸟票: ¥99, 普通票: ¥149, VIP票: ¥399', '2026-03-19 23:59:59', 1);

-- 插入示例子活动
INSERT INTO `sub_activities` (`activity_id`, `sub_name`, `start_time`, `end_time`, `location`, `description`, `sort_order`) VALUES
(1, '科技论坛开幕式', '2026-03-20 09:00:00', '2026-03-20 10:30:00', '主会场A厅', '博览会正式开幕，邀请行业领袖致辞', 1),
(1, '人工智能专场', '2026-03-20 14:00:00', '2026-03-20 17:00:00', 'B厅会议室', '探讨AI技术在各行业的应用', 2),
(1, '企业路演', '2026-03-21 10:00:00', '2026-03-21 12:00:00', '路演大厅', '初创企业项目展示与融资对接', 3);

-- 插入示例标签
INSERT INTO `activity_tags` (`activity_id`, `tag_name`) VALUES
(1, '科技'),
(1, '创新'),
(1, '博览会'),
(1, '人工智能'),
(1, '企业路演');
