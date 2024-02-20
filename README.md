## Testing

As FFmpeg-API makes frequest use of FFmpeg, a Dockerfile has been provided to build an image when natively contains FFmpeg and can easily run the suite of tests via PyTest

To build the test image, run:

    docker build -t ffmpeg-api-test -f Dockerfile.test .

To run the test image, run:

    docker run --rm -it ffmpeg-api-test

This will open a container with a BASH CLI. To perform the test suite, run:

    pytest

To exit the testing environment container, simply run:

    exit