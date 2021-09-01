# CMakeList.txt : CMake project for TestServer, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

project(eduwrench_slurm_simulator CXX)


set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE debug)


set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/CmakeModules/")


# Add needed packages
find_package(nlohmann_json 3.2.0 REQUIRED)
#find_package(pugixml)
find_package(SimGrid REQUIRED)
find_library(WRENCH_LIBRARY NAMES wrench)
find_library(WRENCH_PEGASUS_WORKFLOW_PARSER_LIBRARY NAMES wrenchpegasusworkflowparser)
find_library(PUGIXML_LIBRARY NAMES pugixml)

if (ENABLE_BATSCHED)
    find_library(ZMQ_LIBRARY NAMES zmq)
endif()


FIND_PACKAGE( Boost COMPONENTS program_options REQUIRED )
INCLUDE_DIRECTORIES( ${Boost_INCLUDE_DIR} )

include_directories(src/ include/ ${SimGrid_INCLUDE_DIR}/include /usr/local/include /opt/local/include /usr/local/include/wrench)


# Add source to this project's executable.
add_executable (TestServer
    "server.cpp"
    "SimulationThreadState.cpp"
    "SimulationThreadState.h"
    "httplib.h"
    "workflow_manager.h"
    "workflow_manager.cpp")

# Add source to this project's executable.
add_executable (computeRightnowJobSizes
        "compute_rightnow_job_sizes.cpp")

# Add pthreads
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

if (ENABLE_BATSCHED)
target_link_libraries(TestServer
        PRIVATE Threads::Threads
        ${WRENCH_LIBRARY}
        ${WRENCH_PEGASUS_WORKFLOW_PARSER_LIBRARY}
        ${SimGrid_LIBRARY}
        ${PUGIXML_LIBRARY}
        ${Boost_LIBRARIES}
        ${ZMQ_LIBRARY}
        )
else()
target_link_libraries(TestServer
        PRIVATE Threads::Threads
        ${WRENCH_LIBRARY}
        ${WRENCH_PEGASUS_WORKFLOW_PARSER_LIBRARY}
        ${SimGrid_LIBRARY}
        ${PUGIXML_LIBRARY}
        ${Boost_LIBRARIES}
        )
endif()

target_link_libraries(computeRightnowJobSizes
        ${Boost_LIBRARIES}
        )

