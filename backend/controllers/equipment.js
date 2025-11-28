const Equipment = require('../models/Equipment');

exports.listEquipment = async (req, res) => {
  const items = await Equipment.findAll();
  res.json(items);
};

exports.createEquipment = async (req, res) => {
  try {
    const { name, description, brand, quantity } = req.body;
    const image = req.file ? req.file.path : null;
    const item = await Equipment.create({ name, description, brand, quantity, image });
    res.json(item);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};