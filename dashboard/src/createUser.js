const sql = require('mssql');
const bcrypt = require('bcryptjs');

const dbConfig = {
    user: 'finflo123',
    password: 'Li12ghtwood!',
    server: 'finflo123.database.windows.net',
    database: 'finflo',
    options: {
        encrypt: true
    }
};

const createUser = async (username, plainTextPassword) => {
    try {
        let pool = await sql.connect(dbConfig);
        const passwordHash = await bcrypt.hash(plainTextPassword, 10);

        await pool.request()
            .input('username', sql.NVarChar, username)
            .input('passwordHash', sql.NVarChar, passwordHash)
            .query('INSERT INTO Users (Username, PasswordHash) VALUES (@username, @passwordHash)');

        console.log('User created successfully');
    } catch (err) {
        console.error('Database error:', err);
    }
};

// Replace with your desired username and password
createUser('testuser', '123');