-- Kullanıcılar
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'Odendi'
);

-- Paketler
CREATE TABLE IF NOT EXISTS packages (
    package_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    details TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Abonelikler
CREATE TABLE IF NOT EXISTS user_subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    package_id VARCHAR(50) REFERENCES packages(package_id),
    contract_end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Aktif'
);

-- Örnek Mock Veriler
INSERT INTO users (user_id, name, surname, phone, payment_status) VALUES
('U1001', 'Ali', 'Can', '5551234567', 'Odendi'),
('U1002', 'Ayşe', 'Yılmaz', '5559876543', 'Gecikmede');

INSERT INTO packages (package_id, name, price, details) VALUES
('P101', 'SüperNet 50', 250.00, '50Mbps limitsiz internet, 1000 dk konuşma'),
('P102', 'MegaPaket 100', 350.00, '100Mbps limitsiz internet, 2000 dk konuşma'),
('P103', 'EkoPaket 25', 180.00, '25Mbps internet, 10GB mobil kota');

INSERT INTO user_subscriptions (user_id, package_id, contract_end_date, status) VALUES
('U1001', 'P101', '2026-08-01', 'Aktif'),
('U1002', 'P103', '2025-12-01', 'Aktif');