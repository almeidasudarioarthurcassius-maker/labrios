const express = require('express');
const router = express.Router();
const equipmentController = require('../controllers/equipmentController');
const multer = require('multer');

const upload = multer({ dest: 'uploads/' });

router.get('/', equipmentController.listEquipment);
router.post('/', upload.single('image'), equipmentController.createEquipment);

module.exports = router;