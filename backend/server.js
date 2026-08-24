const express = require("express");
const multer = require("multer");
const axios = require("axios");
const cors = require("cors");
const fs = require("fs");
const FormData = require("form-data");


const app = express();

app.use(cors());
app.use(express.json());


// Image upload configuration
const storage = multer.diskStorage({
    destination: function(req, file, cb) {
        cb(null, "uploads/");
    },

    filename: function(req, file, cb) {
        cb(null, Date.now() + "-" + file.originalname);
    }
});


const upload = multer({
    storage: storage
});



// Test route
app.get("/", (req, res) => {
    res.send("Backend Server Running");
});



// Image prediction route
app.post("/predict", upload.single("image"), async (req, res) => {

    try {

        if (!req.file) {
            return res.status(400).json({
                error: "No image uploaded"
            });
        }


        const formData = new FormData();

        formData.append(
            "image",
            fs.createReadStream(req.file.path)
        );


        const response = await axios.post(
            "http://127.0.0.1:5001/predict",
            formData,
            {
                headers: {
                    ...formData.getHeaders()
                }
            }
        );


        res.json(response.data);


    } catch(error) {

        console.log(error.message);

        res.status(500).json({
            error: "Prediction failed"
        });
    }

});



app.listen(5000, () => {
    console.log("Backend running on port 5000");
});