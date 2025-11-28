const Booking = require('../models/Booking');

exports.listBookings = async (req, res) => {
  const bookings = await Booking.findAll();
  res.json(bookings);
};

exports.createBooking = async (req, res) => {
  try {
    const { startDate, endDate, contact, researcherName, EquipmentId } = req.body;
    const booking = await Booking.create({ startDate, endDate, contact, researcherName, EquipmentId });
    res.json(booking);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};