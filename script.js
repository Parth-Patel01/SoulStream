class SoulStreamUploader {
    constructor() {
        this.files = [];
        this.uploadQueue = [];
        this.isUploading = false;
        this.currentUploadIndex = 0;
        this.serverUrl = 'http://192.168.18.20:8080';

        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.selectFilesBtn = document.getElementById('selectFilesBtn');
        this.startUploadBtn = document.getElementById('startUploadBtn');
        this.uploadList = document.getElementById('uploadList');
        this.toastContainer = document.getElementById('toastContainer');
    }

    bindEvents() {
        // File selection
        this.selectFilesBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelection(e.target.files));

        // Upload area events
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // Upload control buttons
        this.startUploadBtn.addEventListener('click', () => this.startUpload());
    }

    handleFileSelection(fileList) {
        const files = Array.from(fileList).filter(file =>
            file.type.startsWith('video/') ||
            file.name.toLowerCase().endsWith('.mp4') ||
            file.name.toLowerCase().endsWith('.mkv') ||
            file.name.toLowerCase().endsWith('.avi') ||
            file.name.toLowerCase().endsWith('.mov') ||
            file.name.toLowerCase().endsWith('.wmv') ||
            file.name.toLowerCase().endsWith('.flv') ||
            file.name.toLowerCase().endsWith('.webm')
        );

        if (files.length === 0) {
            this.showToast('Please select valid video files (MP4, MKV, AVI, MOV, WMV, FLV, WEBM)', 'warning');
            return;
        }

        this.addFilesToQueue(files);
        this.showToast(`Added ${files.length} file(s) to upload queue`, 'success');
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        this.handleFileSelection(files);
    }

    addFilesToQueue(files) {
        files.forEach(file => {
            const uploadItem = {
                file: file,
                id: this.generateId(),
                status: 'pending',
                progress: 0,
                uploadedBytes: 0,
                totalBytes: file.size,
                startTime: null,
                element: null
            };

            this.uploadQueue.push(uploadItem);
            this.createUploadItemElement(uploadItem);
        });

        this.updateButtonStates();
    }

    createUploadItemElement(uploadItem) {
        const item = document.createElement('div');
        item.className = 'upload-item';
        item.id = `upload-${uploadItem.id}`;

        const fileName = uploadItem.file.name;
        const fileSize = this.formatFileSize(uploadItem.file.size);

        item.innerHTML = `
            <div class="upload-item-header">
                <div class="file-name" title="${fileName}">${fileName}</div>
                <div class="file-size">${fileSize}</div>
                <div class="status-icon">
                    <i class="fas fa-clock"></i>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
            <div class="progress-text">
                <span class="progress-percentage">0%</span>
                <span class="progress-speed">0 KB/s</span>
            </div>
        `;

        this.uploadList.appendChild(item);
        uploadItem.element = item;
    }

    updateUploadProgress(uploadItem, progress, speed = null) {
        if (!uploadItem.element) return;

        const progressFill = uploadItem.element.querySelector('.progress-fill');
        const progressPercentage = uploadItem.element.querySelector('.progress-percentage');
        const progressSpeed = uploadItem.element.querySelector('.progress-speed');
        const statusIcon = uploadItem.element.querySelector('.status-icon i');

        progressFill.style.width = `${progress}%`;
        progressPercentage.textContent = `${Math.round(progress)}%`;

        if (speed) {
            progressSpeed.textContent = speed;
        }

        // Update status icon
        if (progress === 100) {
            statusIcon.className = 'fas fa-check';
            uploadItem.element.classList.add('completed');
        } else if (uploadItem.status === 'error') {
            statusIcon.className = 'fas fa-times';
            uploadItem.element.classList.add('error');
        } else if (uploadItem.status === 'uploading') {
            statusIcon.className = 'fas fa-spinner';
        }
    }

    async startUpload() {
        if (this.uploadQueue.length === 0) {
            this.showToast('No files to upload', 'warning');
            return;
        }

        this.isUploading = true;
        this.currentUploadIndex = 0;

        this.updateButtonStates();
        this.showToast('Starting upload...', 'success');

        await this.processUploadQueue();
    }

    async processUploadQueue() {
        while (this.currentUploadIndex < this.uploadQueue.length) {
            const uploadItem = this.uploadQueue[this.currentUploadIndex];

            if (uploadItem.status === 'pending') {
                uploadItem.status = 'uploading';
                uploadItem.startTime = Date.now();

                try {
                    await this.uploadFile(uploadItem);
                    uploadItem.status = 'completed';
                    this.updateUploadProgress(uploadItem, 100);
                } catch (error) {
                    console.error('Upload error:', error);
                    uploadItem.status = 'error';
                    this.updateUploadProgress(uploadItem, uploadItem.progress);
                    this.showToast(`Failed to upload ${uploadItem.file.name}`, 'error');
                }
            }

            this.currentUploadIndex++;
        }

        if (this.currentUploadIndex >= this.uploadQueue.length) {
            this.isUploading = false;
            this.updateButtonStates();
            this.showToast('All uploads completed!', 'success');
        }
    }

    async uploadFile(uploadItem) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            const formData = new FormData();

            formData.append('file', uploadItem.file);
            formData.append('filename', uploadItem.file.name);

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const progress = (e.loaded / e.total) * 100;
                    uploadItem.progress = progress;
                    uploadItem.uploadedBytes = e.loaded;

                    // Calculate speed
                    const elapsed = (Date.now() - uploadItem.startTime) / 1000;
                    const speed = elapsed > 0 ? this.formatFileSize(e.loaded / elapsed) + '/s' : '0 KB/s';

                    this.updateUploadProgress(uploadItem, progress, speed);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    resolve();
                } else {
                    reject(new Error(`Upload failed with status ${xhr.status}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Network error during upload'));
            });

            xhr.addEventListener('abort', () => {
                reject(new Error('Upload aborted'));
            });

            xhr.open('POST', `${this.serverUrl}/upload`);
            xhr.send(formData);
        });
    }

    updateButtonStates() {
        const hasFiles = this.uploadQueue.length > 0;
        const isUploading = this.isUploading;

        this.startUploadBtn.disabled = !hasFiles || isUploading;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        this.toastContainer.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }
}

// Initialize the uploader when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SoulStreamUploader();
});

// Add some utility functions for better user experience
window.addEventListener('beforeunload', (e) => {
    // Warn user if uploads are in progress
    const uploader = window.soulStreamUploader;
    if (uploader && uploader.isUploading) {
        e.preventDefault();
        e.returnValue = 'Uploads are in progress. Are you sure you want to leave?';
        return e.returnValue;
    }
}); 