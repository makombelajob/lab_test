# PentestLab PI - Application Web Symfony + Python

## 📋 Description

PentestLab PI est une application web hybride développée avec **Symfony 7.4** et **Python 3**, conçue pour la gestion d'un laboratoire de tests de pénétration. L'application combine la puissance du framework PHP Symfony pour la partie web et des scripts Python pour les opérations de traitement de données et d'interaction avec la base de données.

## 🏗️ Architecture

### Stack Technique

- **Backend Web** : Symfony 7.4 (PHP 8.2+)
- **Scripts** : Python 3 avec environnement virtuel
- **Base de données** : MySQL 8.0
- **Serveur Web** : Apache 2.4
- **Containerisation** : Docker & Docker Compose
- **ORM** : Doctrine
- **Templates** : Twig
- **Sécurité** : Symfony Security Bundle

### Structure du Projet

```
pentestlab-pi/
├── app/                          # Application Symfony principale
│   ├── src/
│   │   ├── Controller/          # Contrôleurs Symfony
│   │   ├── Entity/              # Entités Doctrine (User, Scan, Payment, etc.)
│   │   ├── Repository/          # Repositories Doctrine
│   │   └── Form/                # Formulaires Symfony
│   ├── templates/               # Templates Twig
│   ├── scripts/                 # Scripts Python
│   │   ├── db/
│   │   │   └── mysql.py        # Module de connexion MySQL
│   │   ├── import_test.py       # Script de test d'import
│   │   └── test.py              # Script de test
│   ├── config/                  # Configuration Symfony
│   ├── public/                  # Point d'entrée public
│   └── migrations/              # Migrations Doctrine
├── php/
│   └── Dockerfile              # Image Docker PHP/Apache avec Python
├── apache/
│   └── default.conf            # Configuration Apache
└── docker-compose.yaml         # Orchestration Docker
```

## 🔄 Fonctionnement Symfony + Python

### Intégration Python dans Symfony

L'application utilise le composant **Symfony Process** pour exécuter des scripts Python depuis les contrôleurs PHP. Voici comment cela fonctionne :

1. **Exécution via Process** : Les contrôleurs Symfony (ex: `TestPyController`) utilisent `Symfony\Component\Process\Process` pour lancer des scripts Python.

2. **Environnement Python** : Un environnement virtuel Python est configuré dans le conteneur Docker à `/opt/venv/` avec les dépendances nécessaires :
    - `mysql-connector-python` : Connexion à MySQL
    - `numpy` : Calculs numériques
    - `requests` : Requêtes HTTP
    - `python-dotenv` : Gestion des variables d'environnement

3. **Connexion à la base de données** : Les scripts Python utilisent le module `db/mysql.py` qui :
    - Lit la variable d'environnement `DATABASE_URL` ou utilise des variables individuelles
    - Se connecte à MySQL via `mysql-connector-python`
    - Partage la même base de données que Symfony/Doctrine

4. **Flux de données** :
   ```
   Utilisateur → Symfony Controller → Process Python → MySQL
                                    ↓
                              Retour JSON/String
                                    ↓
                              Affichage Twig
   ```

### Exemple d'utilisation

Dans `TestPyController.php` :
```php
$process = new Process(['/opt/venv/bin/python3', '/var/www/html/scripts/import_test.py']);
$process->run();
$output = $process->getOutput();
```

Le script Python peut alors interagir avec la base de données MySQL partagée.

## 🚀 Installation Locale

### Prérequis

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git**

### Étapes d'installation

#### 1. Cloner le dépôt

```bash
git clone https://github.com/makombelajob/pentestlab-pi.git
cd pentestlab-pi
```

#### 2. Configuration de l'environnement

Créez un fichier `.env` dans le dossier `app/` avec la configuration suivante :

```env
# Environnement
APP_ENV=dev
APP_SECRET=your-secret-key-here

# Base de données
DATABASE_URL="mysql://admin:admin7791@database:3306/pentest_lab_pi?serverVersion=8.0"
# Ou variables individuelles :
# DATABASE_HOST=database
# DATABASE_PORT=3306
# DATABASE_USER=admin
# DATABASE_PASSWORD=admin7791
# DATABASE_NAME=pentest_lab_pi
```

#### 3. Construction et démarrage des conteneurs

```bash
# Construire les images Docker
docker-compose build

# Démarrer les services
docker-compose up -d
```

Cette commande démarre :
- **php_pi** : Conteneur PHP/Apache avec Symfony (port 8080)
- **mysql_pi** : Base de données MySQL (port 3306)
- **pma_pi** : phpMyAdmin (port 8081)
- **mailhog_pi** : MailHog pour les emails (port 8025)

#### 4. Installation des dépendances PHP

```bash
# Entrer dans le conteneur PHP
docker exec -it php_pi bash

# Installer les dépendances Composer
cd /var/www/html
composer install
```

#### 5. Configuration de la base de données

```bash
# Toujours dans le conteneur PHP
# Créer la base de données (si nécessaire)
php bin/console doctrine:database:create

# Exécuter les migrations
php bin/console doctrine:migrations:migrate
```

#### 6. Vérification de l'installation

- **Application web** : http://localhost:8080
- **phpMyAdmin** : http://localhost:8081
- **MailHog** : http://localhost:8025

### Installation sans Docker (développement local)

Si vous préférez installer localement sans Docker :

#### Prérequis locaux

- PHP 8.2+
- Composer
- MySQL 8.0
- Python 3.8+
- Apache 2.4 ou serveur PHP intégré

#### Étapes

1. **Installer les dépendances PHP** :
```bash
cd app
composer install
```

2. **Créer l'environnement virtuel Python** :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install mysql-connector-python numpy requests python-dotenv
```

3. **Configurer la base de données** :
    - Créer une base de données MySQL nommée `pentest_lab_pi`
    - Configurer `DATABASE_URL` dans `.env`

4. **Exécuter les migrations** :
```bash
php bin/console doctrine:database:create
php bin/console doctrine:migrations:migrate
```

5. **Démarrer le serveur Symfony** :
```bash
cd ..    # Racine du projet
# sur windows
docker compose up --build
# ou sur Linux
sudo docker-compose up --build
```

## 📦 Services Docker

### php_pi (PHP/Apache + Python)

- **Port** : 8080
- **Image** : Construite depuis `php/Dockerfile`
- **Fonctionnalités** :
    - PHP 8.4 avec extensions (mysqli, pdo_mysql, intl, gd, etc.)
    - Apache avec mod_rewrite
    - Composer installé
    - Symfony CLI installé
    - Python 3 avec venv à `/opt/venv/`
    - Volume monté : `./app:/var/www/html`

### mysql_pi (MySQL)

- **Port** : 3306
- **Image** : mysql:8.0
- **Identifiants par défaut** :
    - User : `admin`
    - Password : `admin7791`
    - Database : `pentest_lab_pi`
    - Root Password : `admin77911`

### pma_pi (phpMyAdmin)

- **Port** : 8081
- **Image** : phpmyadmin:latest
- **Accès** : Interface web pour gérer MySQL

### mailhog_pi (MailHog)

- **Port** : 8025
- **Image** : mailhog/mailhog
- **Usage** : Capture les emails envoyés par l'application en développement

## 🛠️ Commandes Utiles

### Docker

```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f

# Reconstruire après modification du Dockerfile
docker-compose build --no-cache php
docker-compose up -d

# Accéder au conteneur PHP
docker exec -it php_pi bash

# Accéder au conteneur MySQL
docker exec -it mysql_pi mysql -u admin -padmin7791 pentest_lab_pi
```

### Symfony

```bash
# Dans le conteneur PHP
cd /var/www/html

# Créer une migration
php bin/console make:migration

# Exécuter les migrations
php bin/console doctrine:migrations:migrate

# Créer un contrôleur
php bin/console make:controller

# Vider le cache
php bin/console cache:clear

# Créer un utilisateur
php bin/console make:user
```

### Python

```bash
# Dans le conteneur PHP
# Tester un script Python
/opt/venv/bin/python3 /var/www/html/scripts/test.py

# Activer l'environnement virtuel (si besoin)
source /opt/venv/bin/activate
```

## 📁 Entités Principales

L'application utilise Doctrine ORM avec les entités suivantes :

- **User** : Gestion des utilisateurs avec authentification
- **Scan** : Scans de sécurité effectués
- **ResultScan** : Résultats des scans
- **Vulnerabilty** : Vulnérabilités détectées
- **Payment** : Gestion des paiements

## 🔐 Sécurité

- Authentification via Symfony Security Bundle
- Hashage des mots de passe (auto)
- Protection CSRF activée
- Sessions sécurisées
- Validation des formulaires

## 🧪 Tests

### Tester l'intégration Python

Accédez à : http://localhost:8080/test/py

Cette route exécute le script `scripts/import_test.py` et affiche le résultat.

## 📝 Notes de Développement

### Ajouter un nouveau script Python

1. Créer le script dans `app/scripts/`
2. Utiliser `db/mysql.py` pour la connexion :
```python
from db.mysql import get_connection

conn = get_connection()
cursor = conn.cursor()
# Votre code ici
cursor.close()
conn.close()
```

3. L'appeler depuis un contrôleur Symfony :
```php
use Symfony\Component\Process\Process;

$process = new Process(['/opt/venv/bin/python3', '/var/www/html/scripts/votre_script.py']);
$process->run();
$output = $process->getOutput();
```

### Variables d'environnement Python

Les scripts Python peuvent accéder aux variables d'environnement définies dans Docker Compose ou `.env` via `os.getenv()`.

## 🐛 Dépannage

### Le conteneur PHP ne démarre pas

```bash
docker-compose logs php
# Vérifier les erreurs et reconstruire si nécessaire
docker-compose build --no-cache php
```

### Erreur de connexion à la base de données

- Vérifier que MySQL est démarré : `docker-compose ps`
- Vérifier les identifiants dans `docker-compose.yaml` et `.env`
- Tester la connexion : `docker exec -it mysql_pi mysql -u admin -padmin7791`

### Scripts Python ne fonctionnent pas

- Vérifier que le venv existe : `docker exec php_pi ls -la /opt/venv/bin/`
- Vérifier les permissions : `docker exec php_pi chmod +x /var/www/html/scripts/*.py`
- Tester manuellement : `docker exec php_pi /opt/venv/bin/python3 /var/www/html/scripts/test.py`

### Problèmes de permissions

```bash
# Donner les permissions au dossier var/
docker exec php_pi chmod -R 777 /var/www/html/var
```

## 📚 Ressources

- [Documentation Symfony](https://symfony.com/doc/7.4/)
- [Documentation Doctrine](https://www.doctrine-project.org/)
- [Documentation Docker](https://docs.docker.com/)
- [Documentation Python mysql-connector](https://dev.mysql.com/doc/connector-python/en/)

## 📄 Licence

Propriétaire

---

**Développé avec ❤️ pour PentestLab PI**

