cmake_minimum_required(VERSION 3.12) # 3.15
project(GSI-RADS)

set(CMAKE_CXX_STANDARD 17)

include_directories(.)

#add_executable(GSI-RADS)

set_target_properties(GSI-RADS PROPERTIES
        CXX_STANDARD 17
        CXX_EXTENSIONS OFF
        )

include(Package.cmake)