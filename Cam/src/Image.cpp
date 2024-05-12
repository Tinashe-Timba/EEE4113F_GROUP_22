// Standard library includes
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iterator>
#include <numeric>
#include <vector>
#include <iostream>

// External libraries include
#define STB_IMAGE_IMPLEMENTATION
#include "stb/stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb/stb_image_write.h"
#include <boost/filesystem.hpp>

// Local includes
#include "Image.hpp"
namespace fs = boost::filesystem;

Image::Image(std::string filename) {
  fs::path image_path{filename};
  if (fs::exists(image_path)) {
    if (read(filename)) {
      // update the size of the image
      size = height * width * channels;
      std::cout << "Image successfully read\n";
    } else {
      std::cout << "Image failed to load\n";
    }
  } else {
    std::cerr << "File path does not exists";
    std::exit(EXIT_FAILURE);
  }
}

Image::Image(int width, int height, int channels)
    : width{width}, height{height}, channels{channels} {
  size = height * width * channels;
  image_data.reserve(size);
}

bool Image::read(std::string filename) {
  uint8_t *data = stbi_load(filename.c_str(), &width, &height, &channels, 0);
  if (data == nullptr) {
    return false;
  } else {
    image_data = std::vector<uint8_t>(data, data + width * channels * height);
    return true;
  }
}

Image::ImageType Image::get_file_type(std::string filename) {
  size_t last_pos_dot = filename.find_last_of('.');
  size_t dot_not_found = std::string::npos;

  if (last_pos_dot == dot_not_found) {
    std::cerr << "Incorrect file name\n";
    std::exit(EXIT_FAILURE);
  } else {
    std::string file_ext = filename.substr(last_pos_dot + 1);
    if (file_ext == "png") {
      return PNG;
    } else if (file_ext == "jpg") {
      return JPG;
    } else if (file_ext == "bmp") {
      return BMP;
    } else if (file_ext == "tga") {
      return TGA;
    } else {
      return INVALID;
    }
  }
}

bool Image::write(std::string filename) {
  ImageType image_type = get_file_type(filename);
  int write_ret;
  switch (image_type) {
  case PNG:
    write_ret = stbi_write_png(filename.c_str(), width, height, channels,
                               image_data.data(), width * channels);
    break;
  case JPG:
    write_ret = stbi_write_jpg(filename.c_str(), width, height, channels,
                               image_data.data(), 100);
    break;
  case BMP:
    write_ret = stbi_write_bmp(filename.c_str(), width, height, channels,
                               image_data.data());
    break;
  case TGA:
    write_ret = stbi_write_tga(filename.c_str(), width, height, channels,
                               image_data.data());
    break;
  case INVALID:
    std::cerr << "Invalid extension\n";
    std::exit(EXIT_FAILURE);
  default:
    break;
  }
  return write_ret != 0;
}
void Image::to_gray_scale(Image &target){
  // only handle 3 channel color image
  if (channels != 3){
    std::cerr << "Only 3-channel RGB image can be converted to gray\n";
    std::exit(EXIT_FAILURE);
  }
  // apparently stbi_load, returns gamma compressed image, so we are 
  // using weights based on nonlinear images
  auto weighted_sum = [this](uint8_t& r, uint8_t& g, uint8_t& b) -> uint8_t{
    double val = red_scale*r + green_scale*g + blue_scale*b;
    return static_cast<uint8_t>(std::round(val));
  };
  auto it = image_data.begin();
  auto stop = image_data.end();
  while (it != stop){
    uint8_t gray = weighted_sum(*it, *std::next(it,1), *std::next(it,2));
    target.image_data.push_back(gray);
    std::advance(it,3);
  }

}
void Image::gaussian(std::vector<double>& kernel, int k_width, double sigma){
  if (k_width == 1 || k_width%2==0){
    std::cerr << "kernel size must be odd and greater than 1!!\n";
    std::exit(EXIT_FAILURE);
  }
  int k_half = k_width/2;
  for (int i = -k_half; i <= k_half; i++){
    double pow = i*i/(2*sigma*sigma);
    kernel[i+k_half] = std::exp(-pow);
  }
}
void Image::median(Image& blurred){
  int k_width = 11;
  int k_half = k_width/2;
  std::vector<uint8_t> win(k_width*k_width,0);
  for (int i = 0; i < height; i++){
    for (int j = 0; j < width; j++){
      for (int k = -k_half; k <= k_half; k++){
        for (int l = -k_half; l <= k_half; l++){
          int row = i + k;
          int col = j + l;
          row = ((row <0) ? 0 : (row >= height) ? height- 1 : row);
          col = ((col <0) ? 0 : (col >= width)  ? width- 1 : col);
          win.push_back(image_data[row*width + col]);
        }
      }
      std::sort(win.begin(),win.end());
      blurred.image_data.push_back(win[(k_width*k_width-1)/2]);
      win.clear();
    }
  }
}
void Image::convolve(Image& blurred,int channel,  std::vector<double>& kernel){
  int k_width = kernel.size();

  // temporary vector to store intermediate data
  std::vector<uint8_t> temp;
  temp.reserve(size);
  uint8_t* ptemp = temp.data();
  uint8_t* pimage = image_data.data();

  // compute sum of kernel elements
  double k_sum = std::accumulate(kernel.begin(), kernel.end(), 0.0);
  int k_half = k_width/2;
  // apply n by 1 kernel
  for (int row = 0; row < height; row++){
    for (int col = 0; col < width; col++){
        // holds convolution sum
        double sum = 0.0;
        for (int k = -k_half; k<=k_half; k++){
          int roweighted_neigh = row + k;
          // if beyond bounds, reflect about centre
          if (roweighted_neigh >= height || roweighted_neigh < 0){
            roweighted_neigh = row - k;
          }
          //offset
          int offset = (roweighted_neigh*width + col)*channels + channel;
          // compute the sum
          sum += kernel[k_half + k]*pimage[offset];
        }
        // store the value at corresponding position
        //temp.push_back(static_cast<uint8_t>(std::round(sum/k_sum)));
        ptemp[(row*width+ col)*channels + channel] = static_cast<uint8_t>(std::round(sum/k_sum));
    }
  }
  // pointer to output image data
  uint8_t* pblurred = blurred.image_data.data();
  // apply 1 by n kernel
  for (int row = 0; row < height; row++){
    for (int col = 0; col < width; col++){
        // holds convolution sum
        double sum = 0.0;
        for (int k = -k_half; k<=k_half; k++){
          int col_neigh = col + k;
          // if beyond bounds, reflect about centre
          if (col_neigh > width || col_neigh < 0){
            col_neigh = col - k;
          }
          //offset
          int offset = (row*width + col_neigh)*channels + channel;
          // compute the sum
          sum += kernel[k_half + k]*pimage[offset];
        }
        // store the value at corresponding position
        pblurred[(row*width+ col)*channels + channel] = static_cast<uint8_t>(std::round(sum/k_sum));
    }
  }
  
}
void Image::filter(Image& blurred, std::vector<double>& kernel,bool gaussain){
  // create special kernel gaussian filter
  if (gaussain == true){
    double sigma;
    if (kernel.at(0) != 0){
      sigma = kernel.at(0);
      std::cout << sigma << "\n";
    }
    else {
      // default standard deviation
      sigma = 4;
    }
    gaussian(kernel,kernel.size(), sigma);
  }
  // apply filter
  if (channels == 1){
     convolve(blurred, 0,  kernel);
  }
  else if (channels == 3){
      // red channel
      convolve(blurred, 0,  kernel);
      // green channel
      convolve(blurred, 1,  kernel);
      // blue channel
      convolve(blurred, 2,  kernel);
  }
  else {
    // message
  }
}
void Image::absolute_diff(Image& second_op, Image& out){
  // compute absolute difference
  std::transform(image_data.begin(), image_data.end(), second_op.image_data.begin(),
    out.image_data.begin(), [](int first, int sec)-> int{
      return std::abs(first - sec);
    });
}
void Image::hist(std::vector<double>& hist_arr, int channel){
  // if color do histogram for each channel separately
  for (long i = channel; i < size; i+=channels){
      hist_arr[image_data[i]] += 1;
  }
}
void Image::otsu_1d(Image& out){
  // get automatic threshold value
  uint8_t thresh = calc_otsu_thresh_1d();
  uint8_t max = 255;
  uint8_t min = 0;
  std::cout << "Thresh: " << thresh << "\n";
  // apply threshold
  for (int i = 0; i < height; i++){
    for (int j = 0; j < width; j++){
      uint8_t pixel = ((image_data[i*width+j]) >= thresh ? max:min);
      out.image_data.push_back(pixel);
      //if ( pixel == 255) std::cout << static_cast<uint16_t>(pixel) << " \n";
    }
  }
}

uint8_t Image::calc_otsu_thresh_1d(){
  // 1. compute the histogram
  std::vector<double> hist_(bins);
  hist(hist_,0);
  // 2. normalize the historgram
  double tot = static_cast<double>(size);
  std::transform(hist_.begin(), hist_.end(), hist_.begin(), [&tot](double val) -> double {
    // divide each pixel by total elements
    return val/tot;
  });
  // weighted sum look up table
  std::vector<double> summed_table(bins);
  for (int i = 1; i < bins; i++){
    summed_table[i] = summed_table[i-1] + hist_[i]*i;
  }
  // threshold to be computed
  int thresh = 0;
  // inter-class variance
  double variance{};
  // classes probabilities
  double P1{};
  double P2{};
  //classes means
  double m1{};
  double m2{};
  // weighted sums for each class
  double weighted_sum1{};
  double weighted_sum2{};
  // maximum variance
  double max_var = 0;
  for (int i = 1; i <= bins; i++){
    // 3. get probability for each class
    P1 += hist_[i-1];
    // we have normalized histogram, hence P2 = 1 - P1
    P2 = 1 - P1; 

    // 4. calculate weighted sums
    weighted_sum1 = summed_table[i-1];
    weighted_sum2 = summed_table[bins-1] - summed_table[i-1];
    // 5. compute means
    m1 = weighted_sum1/P1;
    m2 = weighted_sum2/P2;

    // 6. compute inter-class variance
    variance = P1*P2*std::pow(m1-m2,2);
    // 7. maximise inter class variance
    if (variance >= max_var){
        max_var = variance;
        thresh = i;
    }
 }
 return thresh;
}

void Image::thresh(Image& out, uint8_t T){
  uint8_t max = 255;
  uint8_t min = 0;
  std::transform(image_data.begin(), image_data.end(), out.image_data.begin(), 
  [&max, &min, &T](uint8_t pixel ) -> uint8_t {
      return ((pixel ) >= T ? max:min );
  });
}

bool Image::detect(){
  int tot = std::count_if(image_data.begin(), image_data.end(), [](uint8_t val) {return val == 255;});
  return tot >= 300;
}
