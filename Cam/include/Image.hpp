// Standard library include
#include <cmath>
#include <string>
#include <cstdint>
#include <vector>
class Image {
public:
  /**
   * @brief enum type for image extension type
   * 
   */
  enum ImageType { PNG, JPG, BMP, TGA, INVALID };
  // number of rows/height of the image
  int height;
  // number of columns/width of an image
  int width;
  // number of channels in the image
  int channels;

  /**
   * @brief Construct a new Image object
   * 
   * @param filename path to full image path, currently supports jpg,png,tga,bmp
   */
  Image(std::string filename);
  /**
   * @brief Construct a new Image object
   * 
   * @param width number of columns in an image
   * @param height number of rows in an image
   * @param channels number of channels
   */
  Image(int width, int height, int channels);
  /**
   * @brief save image to disk
   * 
   * @param filename path to where image is to be stored
   * @return true, if image was written successfully
   * @return false , if image extension is invalid
   */
  bool write(std::string filename);;
  /**
   * @brief converts RGB image to gray scale
   * 
   * @param target reference to Image object to store gray scale image
   */
  void to_gray_scale(Image &target);
  /**
   * @brief Computes absolute difference between two Images
   * 
   * @param second_op Image object to subtract from this Image
   * @param out       Output Image to store the difference
   */
  void absolute_diff(Image& second_op, Image& out);
  /**
   * @brief Apply global thresholding using Otsu's method
   * 
   * @param out Binary image to store thresholded image
   */
  void otsu_1d(Image& out);
  void thresh(Image& out, uint8_t T);
  /**
   * @brief apply a separable filter to an image
   * 
   * @param blurred output image
   * @param kernel  a 1D kernel to be used, if gaussain all entries should be zero and std dev at 0
   * @param gaussain whether its gaussian or not
   */
  void filter(Image& blurred, std::vector<double>& kernel, bool gaussain);
  void median(Image& blurred);
  bool detect();
  // vector to hold image data
  std::vector<uint8_t> image_data;
  // total number of pixels in the image
  std::size_t size;
private:
    // weights used to convert gamma corrected rgb to gray scale based on luminance
    static constexpr double red_scale = 0.2627;
    static constexpr double green_scale = 0.678;
    static constexpr double blue_scale = 0.0593;
    // intensity levels for 8 bits
    static constexpr int bins = 256;
    // helper functions
  /**
    * @brief Get the file type of the image to be stored
    * 
    * @param filename image file nane
    * @return ImageType , enum type indicating image type
    */
  ImageType get_file_type(std::string filename);
    /**
     * @brief creates a 1D gaussian, but ignores the scaling
     * 
     * @param kernel vector to store gaussain values
     * @param k_width size of the kernel
     * @param sigma standard deviation of the kernel
     */
    void gaussian(std::vector<double>& kernel, int k_width, double sigma);
    /**
     * @brief convolves a separable kernel with image
     * 
     * @param blurred Image reference to store blurred image
     * @param channel Channel to apply blurring
     * @param k_width  kernel width
     */
    void convolve(Image& blurred, int channel, std::vector<double>& kernel);
    /**
     * @brief Computes histogram for 1 channel of image
     * 
     * @param hist_arr reference to image to store histogram values
     * @param channel  channel to compute histogram for (0, 1 , 2)
     */
    void hist(std::vector<double>& hist_arr, int channel);
    /**
     * @brief finds otsu's optimum threshold by maximising inter-class variance
     * 
     * @return uint8_t optimum threshold value
     */
    uint8_t calc_otsu_thresh_1d();
    /**
    * @brief reads an image from the path
    * 
    * @param filename full path to the image
    * @return true if image is successfully read
    * @return false if image is not read successfully
    */
    bool read(std::string filename); 
};
