#pragma once

#include <queue>
#include <mutex>
#include <condition_variable>

template<typename T> class BlockingQueue {
public:
    void push(T const& _data)
    {
        {
            std::lock_guard<std::mutex> lock(guard);
            queue.push(_data);
        }
        signal.notify_one();
    }

//    bool empty() const
//    {
//        std::lock_guard<std::mutex> lock(guard);
//        return queue.empty();
//    }

    bool tryPop(T& _value)
    {
        std::lock_guard<std::mutex> lock(guard);
        if (queue.empty())
        {
            return false;
        }

        _value = queue.front();
        queue.pop();
        return true;
    }

    void waitAndPop(T& _value)
    {
        std::unique_lock<std::mutex> lock(guard);
        while (queue.empty())
        {
            signal.wait(lock);
        }

        _value = queue.front();
        queue.pop();
    }


private:
    std::queue<T> queue;
    mutable std::mutex guard;
    std::condition_variable signal;
};