function PCMPlayer(option) {
    this.init(option)
}

PCMPlayer.prototype.init = function (option) {
    let defaults = {
        encoding: '16bitInt',
        channels: 1,
        sampleRate: 8000,
        maxDelay: 500,
    }
    this.option = Object.assign({}, defaults, option);
    this.maxValue = this.getMaxValue()
    this.typedArray = this.getTypedArray()
    this.createContext()
    this.delay = 0
}

PCMPlayer.prototype.getMaxValue = function () {
    var encodings = {
        '8bitInt': 128,
        '16bitInt': 32768,
        '32bitInt': 2147483648,
        '32bitFloat': 1
    }

    return encodings[this.option.encoding] ? encodings[this.option.encoding] : encodings['16bitInt'];
}

PCMPlayer.prototype.getTypedArray = function () {
    var typedArrays = {
        '8bitInt': Int8Array,
        '16bitInt': Int16Array,
        '32bitInt': Int32Array,
        '32bitFloat': Float32Array
    }

    return typedArrays[this.option.encoding] ? typedArrays[this.option.encoding] : typedArrays['16bitInt'];
};

PCMPlayer.prototype.createContext = function () {
    this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    this.gainNode = this.audioCtx.createGain();
    this.gainNode.gain.value = 1;
    this.gainNode.connect(this.audioCtx.destination);
    this.startTime = this.audioCtx.currentTime;
    this.hangOn = false;
};

PCMPlayer.prototype.isTypedArray = function (data) {
    return (data.byteLength && data.buffer && data.buffer.constructor == ArrayBuffer);
};

PCMPlayer.prototype.feed = function (data) {
    if (!this.isTypedArray(data)) return;
    data = this.getFormatedValue(data);

    let bufferSource = this.audioCtx.createBufferSource(),
        length = data.length / this.option.channels,
        audioBuffer = this.audioCtx.createBuffer(this.option.channels, length, this.option.sampleRate),
        audioData,
        channel,
        offset,
        i;
    for (channel = 0; channel < this.option.channels; channel++) {
        audioData = audioBuffer.getChannelData(channel);
        offset = channel;
        for (i = 0; i < length; i++) {
            audioData[i] = data[offset];
            offset += this.option.channels;
        }
    }

    // reset delay
    if (this.hangOn) {
        if (this.audioCtx.currentTime < this.startTime) {
            return
        } else {
            this.hangOn = false
        }
    }

    if (this.startTime < this.audioCtx.currentTime) {
        this.startTime = this.audioCtx.currentTime;
    }

    this.delay = this.startTime - this.audioCtx.currentTime;
    if (this.delay > this.option.maxDelay) {
        this.hangOn = true
    }

    bufferSource.buffer = audioBuffer;
    bufferSource.connect(this.gainNode);
    bufferSource.start(this.startTime);
    this.startTime += audioBuffer.duration;
    // console.log(this.audioCtx.currentTime, this.startTime, audioBuffer.duration);
};

PCMPlayer.prototype.getFormatedValue = function (data) {
    var data = new this.typedArray(data.buffer),
        float32 = new Float32Array(data.length),
        i;

    for (i = 0; i < data.length; i++) {
        float32[i] = data[i] / this.maxValue;
    }
    return float32;
};

PCMPlayer.prototype.volume = function (volume) {
    this.gainNode.gain.value = volume;
};

PCMPlayer.prototype.destroy = function () {
    this.audioCtx.close()
    this.audioCtx = null;
}