# CMakeList.txt : CMake project for TestServer, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

project(wrench-cssi-poc CXX)

add_definitions("-Wall -Wno-unused-variable -Wno-unused-private-field")

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE debug)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/CmakeModules/")

add_custom_command(
        OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/include/REST_API.h
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_REST_API.py ${CMAKE_CURRENT_SOURCE_DIR}/include/REST_API.h.in ${CMAKE_CURRENT_SOURCE_DIR}/include/REST_API.h ${CMAKE_CURRENT_SOURCE_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/doc/index.html
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/include/REST_API.h.in
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/src/SimulationController.cpp
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/src/SimulationDaemon.cpp
        COMMENT "Generating REST API code"
        VERBATIM
)

# Add needed packages
find_package(SimGrid REQUIRED)
find_package(Boost COMPONENTS program_options REQUIRED)
find_package(nlohmann_json 3.2.0 REQUIRED)

find_library(WRENCH_LIBRARY NAMES wrench)
find_library(WRENCH_PEGASUS_WORKFLOW_PARSER_LIBRARY NAMES wrenchpegasusworkflowparser)
#find_library(PUGIXML_LIBRARY NAMES pugixml)

if (ENABLE_BATSCHED)
    find_library(ZMQ_LIBRARY NAMES zmq)
endif()

include_directories(src/ include/ ${Boost_INCLUDE_DIR} ${SimGrid_INCLUDE_DIR}/include /usr/local/include /opt/local/include /usr/local/include/wrench)

# Add source to this project's executable.
add_executable (wrench-daemon
        include/httplib.h
        src/main.cpp
        src/WRENCHDaemon.cpp
        include/WRENCHDaemon.h
        src/SimulationDaemon.cpp
        include/SimulationDaemon.h
        src/SimulationLauncher.cpp
        include/SimulationLauncher.h
        include/SimulationController.h
        src/SimulationController.cpp
        include/BlockingQueue.h
        include/KeyValueStore.h
        include/REST_API.h
       )

# Add pthreads
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

if (ENABLE_BATSCHED)
    target_link_libraries(wrench-daemon
            PRIVATE Threads::Threads
            ${WRENCH_LIBRARY}
            ${WRENCH_PEGASUS_WORKFLOW_PARSER_LIBRARY}
            ${SimGrid_LIBRARY}
            ${PUGIXML_LIBRARY}
            ${Boost_LIBRARIES}
            ${ZMQ_LIBRARY}
            )
else()
    target_link_libraries(wrench-daemon
            PRIVATE Threads::Threads
            ${WRENCH_LIBRARY}
            ${WRENCH_PEGASUS_WORKFLOW_PARSER_LIBRARY}
            ${SimGrid_LIBRARY}
            ${PUGIXML_LIBRARY}
            ${Boost_LIBRARIES}
            )
endif()

