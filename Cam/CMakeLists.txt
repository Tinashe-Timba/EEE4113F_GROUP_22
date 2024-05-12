cmake_minimum_required(VERSION 3.10)
project(STB)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_SHARED_LIBRARY_PREFIX "")
# Set the project version
set(PROJECT_VERSION 1.0)
# Find the Python library
find_package(PythonLibs 3.9 REQUIRED)

# Find the Boost library
find_package(Boost REQUIRED COMPONENTS filesystem system)
# add pybind11 sub directory
# Set the include directories
include_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${Boost_INCLUDE_DIRS}
  /usr/include/python3.9
  ${CMAKE_CURRENT_SOURCE_DIR}/pybind11/include
)

# Set the source files
set(SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Image.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/bind.cpp
)

# Create a shared library
add_library(image SHARED ${SOURCES})
target_link_libraries(image ${Boost_LIBRARIES} ${PythonLibs_LIBRARIES})
