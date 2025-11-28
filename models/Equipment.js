const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Equipment = sequelize.define('Equipment', {
  id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
  name: { type: DataTypes.STRING, allowNull: false },
  description: { type: DataTypes.STRING },
  brand: { type: DataTypes.STRING },
  quantity: { type: DataTypes.INTEGER, defaultValue: 1 },
  image: { type: DataTypes.STRING } // caminho da imagem
});

module.exports = Equipment;