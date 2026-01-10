<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260110193020 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE exploit (id INT AUTO_INCREMENT NOT NULL, ping_id INT DEFAULT NULL, module VARCHAR(200) DEFAULT NULL, payload VARCHAR(100) DEFAULT NULL, status TINYINT(1) DEFAULT NULL, session_id VARCHAR(50) DEFAULT NULL, output LONGTEXT DEFAULT NULL, proof LONGTEXT DEFAULT NULL, INDEX IDX_8B6D7232470C4B73 (ping_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE ping (id INT AUTO_INCREMENT NOT NULL, user_id INT NOT NULL, hostname VARCHAR(100) DEFAULT NULL, ip_address VARCHAR(18) DEFAULT NULL, status TINYINT(1) DEFAULT NULL, scan_at DATETIME NOT NULL COMMENT \'(DC2Type:datetime_immutable)\', INDEX IDX_25D53DFDA76ED395 (user_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE reconn (id INT AUTO_INCREMENT NOT NULL, ping_id INT NOT NULL, email_found LONGTEXT DEFAULT NULL, user_found LONGTEXT DEFAULT NULL, link_found LONGTEXT DEFAULT NULL, INDEX IDX_9D962BD2470C4B73 (ping_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE scanner (id INT AUTO_INCREMENT NOT NULL, ping_id INT DEFAULT NULL, port INT NOT NULL, service VARCHAR(50) NOT NULL, version VARCHAR(50) DEFAULT NULL, script_vuln LONGTEXT DEFAULT NULL, state VARCHAR(7) NOT NULL, os_detected VARCHAR(30) DEFAULT NULL, description LONGTEXT DEFAULT NULL, INDEX IDX_55EFDF29470C4B73 (ping_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE user (id INT AUTO_INCREMENT NOT NULL, email VARCHAR(180) NOT NULL, roles JSON NOT NULL, password VARCHAR(255) NOT NULL, first_name VARCHAR(50) NOT NULL, last_name VARCHAR(50) NOT NULL, category VARCHAR(20) NOT NULL, created_at DATETIME NOT NULL COMMENT \'(DC2Type:datetime_immutable)\', lastlogin_at DATETIME DEFAULT NULL COMMENT \'(DC2Type:datetime_immutable)\', reset_token VARCHAR(36) DEFAULT NULL, UNIQUE INDEX UNIQ_IDENTIFIER_EMAIL (email), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE messenger_messages (id BIGINT AUTO_INCREMENT NOT NULL, body LONGTEXT NOT NULL, headers LONGTEXT NOT NULL, queue_name VARCHAR(190) NOT NULL, created_at DATETIME NOT NULL COMMENT \'(DC2Type:datetime_immutable)\', available_at DATETIME NOT NULL COMMENT \'(DC2Type:datetime_immutable)\', delivered_at DATETIME DEFAULT NULL COMMENT \'(DC2Type:datetime_immutable)\', INDEX IDX_75EA56E0FB7336F0E3BD61CE16BA31DBBF396750 (queue_name, available_at, delivered_at, id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('ALTER TABLE exploit ADD CONSTRAINT FK_8B6D7232470C4B73 FOREIGN KEY (ping_id) REFERENCES ping (id)');
        $this->addSql('ALTER TABLE ping ADD CONSTRAINT FK_25D53DFDA76ED395 FOREIGN KEY (user_id) REFERENCES user (id)');
        $this->addSql('ALTER TABLE reconn ADD CONSTRAINT FK_9D962BD2470C4B73 FOREIGN KEY (ping_id) REFERENCES ping (id)');
        $this->addSql('ALTER TABLE scanner ADD CONSTRAINT FK_55EFDF29470C4B73 FOREIGN KEY (ping_id) REFERENCES ping (id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE exploit DROP FOREIGN KEY FK_8B6D7232470C4B73');
        $this->addSql('ALTER TABLE ping DROP FOREIGN KEY FK_25D53DFDA76ED395');
        $this->addSql('ALTER TABLE reconn DROP FOREIGN KEY FK_9D962BD2470C4B73');
        $this->addSql('ALTER TABLE scanner DROP FOREIGN KEY FK_55EFDF29470C4B73');
        $this->addSql('DROP TABLE exploit');
        $this->addSql('DROP TABLE ping');
        $this->addSql('DROP TABLE reconn');
        $this->addSql('DROP TABLE scanner');
        $this->addSql('DROP TABLE user');
        $this->addSql('DROP TABLE messenger_messages');
    }
}
