# Odoo Electrical Panel Builder ERP System

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://www.odoo.com/)
[![License](https://img.shields.io/badge/License-LGPL--3.0-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

A comprehensive ERP solution built on Odoo framework, specifically designed for electrical panel manufacturing and assembly companies. This system streamlines operations from quotation to delivery, managing complex bill of materials, manufacturing processes, and electrical component specifications.

## 🚀 Features

### Core Manufacturing Modules
- **Custom Bill of Materials (BOM)** - Manage complex electrical panel configurations with multi-level BOMs
- **Manufacturing Resource Planning (MRP)** - Plan and schedule panel production with material requirements
- **Quality Control** - Integrated testing and certification workflows for electrical panels
- **Work Order Management** - Track assembly progress and technician assignments

### Electrical Industry Specific
- **Component Specifications Database** - Comprehensive catalog of electrical components with technical specifications
- **Panel Configuration Builder** - Interactive tool for designing custom electrical panels
- **Compliance Management** - Track certifications, standards (IEC, UL, CE), and regulatory requirements
- **Technical Documentation** - Generate wiring diagrams, installation guides, and test certificates

### Business Operations
- **Customer Relationship Management (CRM)** - Manage leads, opportunities, and customer communications
- **Sales & Quotations** - Generate detailed quotes with technical specifications and pricing
- **Inventory Management** - Track electrical components, raw materials, and finished panels
- **Purchase Management** - Vendor management and procurement workflows
- **Project Management** - Track custom panel projects from design to installation
- **Accounting & Finance** - Complete financial management with project costing

## 📋 Requirements

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended), Windows 10+, or macOS 10.14+
- **Python**: 3.8 or higher
- **PostgreSQL**: 12.0 or higher
- **Memory**: Minimum 4GB RAM (8GB+ recommended for production)
- **Storage**: 10GB+ available disk space

### Dependencies
```bash
# Core Odoo dependencies
python3-pip
python3-dev
libxml2-dev
libxslt1-dev
libevent-dev
libsasl2-dev
libldap2-dev
build-essential
libpq-dev
libjpeg-dev
libfreetype6-dev
zlib1g-dev
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Seif-Mohammed/Odoo-Electrical-Panel-builder-companis-ERP-System.git
cd Odoo-Electrical-Panel-builder-companis-ERP-System
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv odoo-env
source odoo-env/bin/activate  # On Windows: odoo-env\Scripts\activate

# Install Python dependencies
pip3 install -r requirements.txt
```

### 3. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Create database user
sudo -u postgres createuser -s $USER
sudo -u postgres createdb odoo_electrical_panel
```

### 4. Configure Odoo
```bash
# Copy configuration file
cp odoo.conf.example odoo.conf

# Edit configuration
nano odoo.conf
```

### 5. Initialize Database
```bash
# First-time setup
python3 odoo-bin -c odoo.conf -d odoo_electrical_panel -i base --stop-after-init

# Start Odoo server
python3 odoo-bin -c odoo.conf
```

### 6. Access the System
Open your web browser and navigate to: `http://localhost:8069`

**Default Login:**
- **Email**: admin
- **Password**: admin

## 📁 Project Structure

```
Odoo-Electrical-Panel-builder-companis-ERP-System/
├── odoo/                                    # Odoo core installation
│   └── Custom_addons/                       # Custom modules directory
│       └── app1/                            # Main electrical panel builder module
│           ├── controllers/                 # HTTP controllers and routing
│           │   ├── __init__.py
│           │   └── Manufacturing_entry.py
│           ├── custom_programs/             # Custom business logic programs
│           ├── drawings/                    # CAD drawings and technical files
│           │   └── A02_1000x1700x400.dwg
│           ├── i18n/                       # Internationalization files
│           │   ├── app1.pot                # Translation template
│           │   ├── ar_001.mo               # Arabic translations (compiled)
│           │   └── ar_001.po               # Arabic translations (source)
│           ├── __init__.py                 # Module initialization
│           ├── __manifest__.py             # Module manifest and metadata
│           ├── models/                     # Data models and business logic
│           │   ├── __init__.py
│           │   ├── inventory_auth.py       # Inventory authorization
│           │   ├── manufacturing.py        # Manufacturing processes
│           │   ├── tech_dashboard.py       # Technical dashboard
│           │   └── technical_office.py     # Technical office management
│           ├── reports/                    # Report templates
│           │   └── bom_report.xml          # Bill of Materials report
│           ├── security/                   # Access control and permissions
│           │   ├── ir.model.access.csv     # Model access rights
│           │   └── security.xml            # Security groups and rules
│           ├── static/                     # Static web assets
│           │   ├── description/            # Module description assets
│           │   │   ├── icon.png            # Module icon
│           │   │   └── logo.png            # Company logo
│           │   └── src/                    # Web interface assets
│           │       ├── css/                # Stylesheets
│           │       ├── http/               # HTTP-related assets
│           │       ├── js/                 # JavaScript files
│           │       └── xml/                # XML templates
│           ├── tests/                      # Unit tests
│           │   ├── __init__.py
│           │   ├── test_inventory.py       # Inventory module tests
│           │   └── test_technical_office.py # Technical office tests
│           └── views/                      # User interface definitions
│               ├── inventory_auth_views.xml     # Inventory UI views
│               ├── manufacturing_views.xml      # Manufacturing UI views
│               └── technical_office_views.xml   # Technical office UI views
├── requirements.txt                        # Python dependencies
├── odoo.conf                              # Configuration file
├── run_odoo.sh                            # Server launch script
└── README.md                              # This documentation file
```
## 🔧 Configuration

### Basic Configuration
Edit `odoo.conf` to customize your installation:

```ini
[options]
# Server configuration
xmlrpc_port = 8069
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_password
db_name = odoo_electrical_panel

# Paths
addons_path = ./addons,./odoo/addons
data_dir = ./data

# Logging
log_level = info
logfile = ./logs/odoo.log

# Performance
workers = 2
max_cron_threads = 1
```

### Custom Module Configuration
Enable electrical panel specific modules:
1. Go to Apps menu
2. Remove "Apps" filter
3. Search and install:
   - Electrical Panel Builder
   - Component Management
   - Panel Manufacturing
   - Electrical Compliance

## 📚 Usage

### Quick Start Guide

1. **Set Up Company Information**
   - Configure your electrical panel manufacturing company details
   - Set up warehouses and manufacturing locations

2. **Import Component Catalog**
   - Import electrical components from `data/components_catalog.csv`
   - Configure component specifications and suppliers

3. **Create Your First Panel**
   - Use the Panel Configuration Builder
   - Define BOM with electrical components
   - Set up manufacturing routing

4. **Generate Quotation**
   - Create customer quotation with technical specifications
   - Include compliance requirements and certifications

5. **Process Manufacturing Order**
   - Convert quotation to sales order
   - Generate manufacturing order
   - Track assembly progress

### Key Workflows

#### Panel Design Workflow
1. **Customer Requirements** → 2. **Technical Design** → 3. **BOM Creation** → 4. **Quotation** → 5. **Approval** → 6. **Manufacturing**

#### Quality Control Process
1. **Incoming Inspection** → 2. **In-Process Testing** → 3. **Final Testing** → 4. **Certification** → 5. **Delivery**

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
# Run all tests
python3 odoo-bin -c odoo.conf -d test_database --test-enable --stop-after-init

# Run specific module tests
python3 odoo-bin -c odoo.conf -d test_database --test-enable -i electrical_panel_builder --stop-after-init
```

## 🚀 Deployment

### Production Deployment

1. **Server Setup**
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install nginx postgresql-12 python3-pip

# Configure PostgreSQL for production
sudo -u postgres psql -c "CREATE USER odoo WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "CREATE DATABASE odoo_production OWNER odoo;"
```

2. **Application Deployment**
```bash
# Clone repository
git clone https://github.com/Seif-Mohammed/Odoo-Electrical-Panel-builder-companis-ERP-System.git /opt/odoo

# Set up production configuration
cp /opt/odoo/config/odoo.conf.production /opt/odoo/odoo.conf

# Create systemd service
sudo systemctl enable odoo
sudo systemctl start odoo
```

3. **Web Server Configuration**
Configure Nginx as reverse proxy (see `docs/nginx_config.md`)

## 🤝 Contributing

We welcome contributions to improve the Odoo Electrical Panel Builder ERP System!

### How to Contribute

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit Changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to Branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write comprehensive docstrings for all functions
- Include unit tests for new features
- Update documentation for any changes
- Ensure backward compatibility

### Code Standards
- Use meaningful variable and function names
- Comment complex business logic
- Follow Odoo development guidelines
- Maintain module dependencies properly

## 📄 License

This project is licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0) - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Odoo Community Edition**: LGPL-3.0
- **Python Dependencies**: Various (see requirements.txt)

## 📞 Support & Contact

### Getting Help
- **Documentation**: Check the `docs/` folder for detailed guides
- **Issues**: Report bugs via [GitHub Issues](https://github.com/Seif-Mohammed/Odoo-Electrical-Panel-builder-companis-ERP-System/issues)
- **Discussions**: Join project discussions on GitHub

### Professional Support
For professional support, customization, or training services, please contact:

**Project Maintainer**: Seif Mohammed
- **Email**: [Email](seifmohamed606@gmail.com)
- **LinkedIn**: [LinkedIn Profile](https://www.linkedin.com/in/seifmo/)
- **GitHub**: [@Seif-Mohammed](https://github.com/Seif-Mohammed)

### Community
- **Odoo Community**: [https://www.odoo.com/forum](https://www.odoo.com/forum)



## 🙏 Acknowledgments

- **Odoo SA** - For the amazing ERP framework
- **Electrical Industry Partners** - For requirements and testing
- **Open Source Community** - For continuous support and contributions
- **Beta Testers** - For valuable feedback and bug reports

---

**⭐ If this project helps your electrical panel manufacturing business, please consider giving it a star!**

**🔗 Connect with us on social media for updates and industry insights.**
