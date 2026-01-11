# Lab-Test - Application Web Symfony + Python

## 📋 Description

Lab-Test est une application web hybride développée avec **Symfony 7.4** et **Python 3**, conçue pour la gestion d'un laboratoire de tests de pénétration. L'application combine la puissance du framework PHP Symfony pour la partie web et des scripts Python pour les opérations de traitement de données et d'interaction avec la base de données.

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
lab_test/
├── app/                          # Application Symfony principale
│   ├── src/
│   │   ├── Controller/          # Contrôleurs Symfony
│   │   ├── Entity/              # Entités Doctrine (User, Scan, Payment, etc.)
│   │   ├── Repository/          # Repositories Doctrine
│   │   └── Form/                # Formulaires Symfony
│   ├── templates/               # Templates Twig
│   ├── scripts/                 # Scripts Python
│   │   ├── db/
│   │   │   └── mysql.py         # Module de connexion MySQL
│   │   ├── attack_chains/       # dossier de fichier d'exploit
|   |   |   └── apache.py        # fichier d'exploit apache
|   |   |   └── ssh.py           # fichier d'exploit ssh
│   │   └── engine /             
|   |   |   └── attack_chain.py    # Moteur d'attack chain
|   |   |   └── exploit_engine.py  # moteur d'exploit chain
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

L'application utilise le composant **Symfony shell_exec** pour exécuter des scripts Python depuis les contrôleurs PHP. Voici comment cela fonctionne :

1. **Exécution via shell_exec** : Les contrôleurs Symfony (ex: `PingController`) utilisent `shell_exec` pour lancer des scripts Python.

2. **Environnement Python** : Un environnement virtuel Python est configuré dans le conteneur Docker à `/opt/venv/` avec les dépendances nécessaires :
    - `mysql-connector-python` : Connexion à MySQL
    - `numpy` : Calculs numériques
    - `requests` : Requêtes HTTP
    - `python-dotenv` : Gestion des variables d'environnement
    - `BeautifulSoup` : La bonne lecture des pages html
    - `pymetasploit3` : Pour l'exploitation de vulnéraiblités

3. **Connexion à la base de données** : Les scripts Python utilisent le module `db/mysql_conn.py` qui :
    - Stock les variables d'environnement `DATABASE_URL` ou utilise des variables individuelles
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

Dans `PingController.php` :
```php
$pyBin = '/opt/venv/bin/python3';
$pyModule = 'scripts.ping.pingtarget';
$projectRoot = $this->getParameter('kernel.project_dir');

$command = sprintf(
'cd %s && %s -m %s %d %s 2>&1',
escapeshellarg($projectRoot),
escapeshellcmd($pyBin),
escapeshellarg($pyModule),
$userId,
escapeshellarg($target)
);

$output = shell_exec($command);
```

Le script Python peut alors interagir avec la base de données MySQL partagée. ( En se servant ausi de paramètres passer dans la commande).

## 🚀 Installation Locale

### Prérequis

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git**

### Étapes d'installation

#### 1. Cloner le dépôt

```bash
git clone https://github.com/makombelajob/lab_test.git
cd lab_test
```
#### 2. Configuration de l'environnement

Créez un fichier `.env.local` dans le dossier `app/` avec la configuration suivante :

```env
# Environnement
APP_ENV=dev
APP_SECRET=your-secret-key-here

# Base de données
DATABASE_URL="mysql://admin:admin7791@database:3306/lab_test?serverVersion=8.0"
# Ou variables individuelles :
# DATABASE_HOST=database
# DATABASE_PORT=3306
# DATABASE_USER=admin
# DATABASE_PASSWORD=admin7791
# DATABASE_NAME=lab_test
```

#### 3. Construction et démarrage des conteneurs

```bash
# Construire les images Docker
docker compose build

# Démarrer les services
docker compose up -d
```

Cette commande démarre :
- **php_lab** : Conteneur PHP/Apache avec Symfony (port 8080)
- **mysql_lab** : Base de données MySQL (port 3306)
- **pma_lab** : phpMyAdmin (port 8081)
- **mailhog_lab** : MailHog pour les emails (port 8025)

#### 4. Installation des dépendances PHP

```bash
# Entrer dans la racine du dossier
cd app
composer install

```

#### 5. Configuration de la base de données

```bash
# Entrer dans le conteneur pour faire la migration ( toujours à la racine du dossier )
docker compose exec -it php /bin/bash
php bin/console make:migration
ou
symfony console make:migration

# Exécuter les migrations
php bin/console doctrine:migrations:migrate
ou 
symfony console d:m:m
```

#### 6. Vérification de l'installation

- **Application web** : http://localhost:8080
- **phpMyAdmin** : http://localhost:8081
- **MailHog** : http://localhost:8025


## 📁 Entités Principales

L'application utilise Doctrine ORM avec les entités suivantes :

- **User** : Gestion des utilisateurs avec authentification
- **Ping** : Tester si le serveur réponds
- **Reconn** : Récupérer certaines informations accèssible en ligne
- **Scan** : Scanner les ports pour chercher les Vulnérabilités


## 🔐 Sécurité

- Authentification via Symfony Security Bundle
- Hashage des mots de passe (auto)
- Protection CSRF activée
- Sessions sécurisées
- Validation des formulaires

## 🧪 Tests

### Tester l'intégration Python

Accédez à : http://localhost:8080/

Cette route exécute le script `scripts/*` et affiche le résultat.

## 📝 Notes de Développement

### Ajouter un nouveau script Python

1. Créer le script dans `app/scripts/`
2. Utiliser `db/mysql_conn.py` pour la connexion :
```python
from db.mysql_conn import get_connection

conn = get_connection()
cursor = conn.cursor()
# Votre code ici
cursor.close()
conn.close()
```

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
docker exec php_lab chmod -R 777 /var/www/html/var
```

## 📚 Ressources

- [Documentation Symfony](https://symfony.com/doc/7.4/)
- [Documentation Doctrine](https://www.doctrine-project.org/)
- [Documentation Docker](https://docs.docker.com/)
- [Documentation Python mysql-connector](https://dev.mysql.com/doc/connector-python/en/)

## 📄 Licence

Propriétaire

---

**Développé par JOB-JOHNNY avec ❤️ pour PentestLab**

