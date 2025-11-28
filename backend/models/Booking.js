const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const User = require('./User');
const Equipment = require('./Equipment');

const Booking = sequelize.define('Booking', {
  id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
  startDate: { type: DataTypes.DATE, allowNull: false },
  endDate: { type: DataTypes.DATE, allowNull: false },
  contact: { type: DataTypes.STRING, allowNull: false },
  researcherName: { type: DataTypes.STRING, allowNull: false }
});

// Relacionamentos
User.hasMany(Booking);
Booking.belongsTo(User);

Equipment.hasMany(Booking);
Booking.belongsTo(Equipment);

module.exports = Booking;