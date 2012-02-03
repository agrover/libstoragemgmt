/*
 * Copyright (C) 2011-2012 Red Hat, Inc.
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Author: tasleson
 */

#ifndef LSM_IPC_H
#define LSM_IPC_H

#include <libstoragemgmt/libstoragemgmt_common.h>
#include <yajl/yajl_parse.h>
#include <yajl/yajl_gen.h>
#include <stdint.h>
#include <string>
#include <map>
#include <vector>
#include <sstream>
#include <stdexcept>

//Common serialization

/**
 * Sends and receives payloads, unaware of the contents.
 * Notes:   Not thread safe. i.e. you cannot share the same object with two or
 * more threads.
 */
class LSM_DLL_LOCAL Transport {
public:

    /**
     * Size of the header which immediately proceeds the payload.
     */
    const static int HDR_LEN = 10;

    /**
     * Empty ctor.
     * @return
     */
    Transport();

    /**
     * Class ctor
     * @param socket_desc   Connected socket descriptor.
     */
    Transport(int socket_desc);

    /**
     * Class dtor
     */
    ~Transport();

    /**
     * Sends a message over the transport.
     * @param[in]   msg         The message to be sent.
     * @param[out]  error_code  Errno (only valid if we return -1)
     * @return 0 on success, else -1
     */
    int sendMsg(const std::string &msg, int &error_code);

    /**
     * Received a message over the transport.
     * Note: A zero read indicates that the transport was closed by other side,
     *       no error code will be set in that case.
     * @param error_code    (0 on success, else errno)
     * @return Message on success else 0 size with error_code set (not if EOF)
     */
    std::string recvMsg(int &error_code);

    /**
     * Creates a connected socket (AF_UNIX) to the specified path
     * @param path of the AF_UNIX file to be used for IPC
     * @param error_code    Error reason for the failure (errno)
     * @return -1 on error, else connected socket.
     */
    static int getSocket(const std::string &path, int &error_code);

    /**
     * Closes the transport, called in the destructor if not done in advance.
     * @return 0 on success, else EBADF, EINTR, EIO.
     */
    int close();

private:
    int s; //Socket descriptor
};

/**
 * Generic function to convert Type v into a string.
 * @param v Template type T
 * @return string representation
 */
template <class Type> static std::string to_string(Type v) {
    std::stringstream out;
    out << v;
    return out.str();
}

class LSM_DLL_LOCAL EOFException : public std::runtime_error {
public:
    EOFException(std::string m);
};


/**
 * User defined class for Value errors during serialize / de-serialize.
 */
class LSM_DLL_LOCAL ValueException : public std::runtime_error {
public:
    /**
     * Constructor
     * @param m Exception message
     */
    ValueException(std::string m);
};

class LSM_DLL_LOCAL LsmException : public std::runtime_error {
public:
    LsmException(int code, std::string &msg);


    LsmException(int code, std::string &msg, const std::string &debug_addl,
        const std::string &debug_data_addl);

    ~LsmException() throw ();

    int error_code;
    std::string debug;
    std::string debug_data;
};

/**
 * Represents a value in the serialization.
 */
class LSM_DLL_LOCAL Value {
public:

    /**
     * Different types this class can hold.
     */
    enum value_type {
        null_t, boolean_t, string_t, numeric_t, object_t, array_t
    };

    /**
     * Default constructor creates a "null" type
     */
    Value(void);

    /**
     * Boolean constructor
     * @param v value
     */
    Value(bool v);

    /**
     * Numeric double constructor.
     * @param v value
     */
    Value(double v);

    /**
     * Numeric unsigned 32 constructor
     * @param v value
     */
    Value(uint32_t v);

    /**
     * Numeric signed 32 constructor
     * @param v value
     */
    Value(int32_t v);

    /**
     * Numeric unsigned 64 constructor.
     * @param v value
     */
    Value(uint64_t v);

    /**
     * Numeric signed 64 constructor.
     * @param v value
     */
    Value(int64_t v);

    /**
     * Constructor in which you specify type and initial value as string.
     * @param type  Type this object will hold.
     * @param v value
     */
    Value(value_type type, const std::string &v);

    /**
     * Constructor for char * i.e. string.
     * @param v value
     */
    Value(const char *v);

    /**
     * Constructor for std::string
     * @param v value
     */
    Value(const std::string &v);

    /**
     * Constructor for object type
     * @param v values
     */
    Value(const std::map<std::string, Value> &v);

    /**
     * Constructor for array type
     * @param v array values
     */
    Value(const std::vector<Value> &v);

    /**
     * Serialize Value to json
     * @return
     */
    std::string serialize(void);

    /**
     * Returns the enumerated type represented by object
     * @return enumerated type
     */
    value_type valueType() const;

    /**
     * Overloaded operator for map access
     * @param key
     * @return Value
     */
    Value& operator[](const std::string &key);

    /**
     * Overloaded operator for vector(array) access
     * @param i
     * @return Value
     */
    Value& operator[](uint32_t i);

    /**
     * Returns true if value has a key in key/value pair
     * @return true if key exists, else false.
     */
    bool hasKey(const std::string &k);

    /**
     * Checks to see if a Value contains a valid request
     * @return True if it is a request, else false
     */
    bool isValidRequest(void);

    /**
     * Given a key returns the value.
     * @param key
     * @return Value
     */
    Value getValue(const char* key);


    /**
     * Returns NULL if void type, else ValueException
     * @return NULL
     */
    void * asVoid();

    /**
     * Boolean value represented by object.
     * @return true, false ValueException on error
     */
    bool asBool();

    /**
     * Double value represented by object.
     * @return double value else ValueException on error
     */
    double asDouble();

    /**
     * Signed 32 integer value represented by object.
     * @return integer value else ValueException on error
     */
    int32_t asInt32_t();

    /**
     * Signed 64 integer value represented by object.
     * @return integer value else ValueException on error
     */
    int64_t asInt64_t();

    /**
     * Unsigned 32 integer value represented by object.
     * @return integer value else ValueException on error
     */
    uint32_t asUint32_t();

    /**
     * Unsigned 64 integer value represented by object.
     * @return integer value else ValueException on error
     */
    uint64_t asUint64_t();

    /**
     * String value represented by object.
     * @return string value else ValueException on error
     */
    std::string asString();

    /**
     * key/value represented by object.
     * @return map of key and values else ValueException on error
     */
    std::map<std::string, Value> asObject();

    /**
     * vector of values represented by object.
     * @return vector of array values else ValueException on error
     */
    std::vector<Value> asArray();

private:
    value_type t;
    std::string s;
    std::map<std::string, Value> obj;
    std::vector<Value> array;

    void marshal(yajl_gen g);
};

/**
 * Serialize, de-serialize methods.
 */
class LSM_DLL_LOCAL Payload {
public:
    /**
     * Given a Value returns json representation.
     * @param v Value to serialize
     * @return String representation
     */
    static std::string serialize(Value &v);

    /**
     * Given a json string return a Value
     * @param json  String to de-serialize
     * @return Value
     */
    static Value deserialize(const std::string &json);
};

class LSM_DLL_LOCAL Ipc {
public:
    Ipc();
    Ipc(int fd);
    Ipc(std::string socket_path);
    ~Ipc();

    void sendRequest(const std::string request, const Value &params,
                        int32_t id = 100);
    Value readRequest(void);

    void sendResponse(const Value &response, uint32_t id = 100);
    Value readResponse();

    void sendError(int error_code, std::string msg, std::string debug,
                    uint32_t id = 100);

    Value rpc(const std::string &request, const Value &params, int32_t id = 100);


private:
    Transport t;
};

#endif