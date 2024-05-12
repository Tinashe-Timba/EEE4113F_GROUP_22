#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Image.hpp"

namespace py = pybind11;

PYBIND11_MODULE(image, m) {
    py::class_<Image>(m, "Image")
        .def(py::init<std::string>())
        .def(py::init<int, int, int>())
        // public members
        .def_readwrite("height", &Image::height)
        .def_readwrite("width", &Image::width)
        .def_readwrite("channels", &Image::channels)
        .def_readwrite("size", &Image::height)
        .def_readwrite("image_data", &Image::image_data)
        // public member functions
        .def("write", &Image::write)
        .def("to_gray_scale", &Image::to_gray_scale)
        .def("absolute_diff", &Image::absolute_diff)
        .def("otsu_1d", &Image::otsu_1d)
        .def("thresh", &Image::thresh)
        .def("filter", &Image::filter)
        .def("median", &Image::median)
        .def("detect", &Image::detect);

    // expose enum
    py::enum_<Image::ImageType>(m, "ImageType")
        .value("PNG", Image::PNG)
        .value("JPG", Image::JPG)
        .value("BMP", Image::BMP)
        .value("TGA", Image::TGA)
        .value("INVALID", Image::INVALID);
}
