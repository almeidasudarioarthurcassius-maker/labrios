const express = require('express');
const cors = require('cors');
const sequelize = require('./config/db');

const authRoutes = require('./routes/auth');
const equipmentRoutes = require('./routes/equipment');
const bookingRoutes = require('./routes/booking');

const app = express();
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static('uploads')); // servir imagens

// Rotas
app.use('/api/auth', authRoutes);
app.use('/api/equipment', equipmentRoutes);
app.use('/api/bookings', bookingRoutes);

// Sincronizar DB
sequelize.sync().then(() => {
  console.log('Banco sincronizado');
  app.listen(3000, () => console.log('Servidor rodando na porta 3000'));
}).catch(err => console.error('Erro ao sincronizar DB:', err));