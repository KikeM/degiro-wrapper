FROM debian:stretch-slim

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
WORKDIR /root

# Clear previous sources
RUN rm /var/lib/apt/lists/* -vf \
    # Base dependencies
    && apt-get -y update \
    && apt-get -y dist-upgrade \
    && apt-get -y --force-yes install \
        apt-utils \
        build-essential \
        bzip2 \
        ca-certificates \
        curl \
        git \
        gnupg \
        htop \
        libbz2-dev \
        libfontconfig \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        net-tools \
        make \
        readline-common \
        supervisor \
        vim \
        wget \
        zlib1g-dev \
        xz-utils \
        zsh \
    && curl -sL https://deb.nodesource.com/setup_10.x | bash - \
    && apt-get install -y nodejs \
    && curl https://pyenv.run | bash \
    && echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc \
    && echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc \
    && echo 'if command -v pyenv 1>/dev/null 2>&1; then' >> ~/.bashrc \
    && echo '    eval "$(pyenv init -)"' >> ~/.bashrc \
    && echo 'fi' >> ~/.bashrc \
    && . ~/.bashrc \
    && pyenv install -f 3.6.10 \
    && echo "pyenv global 3.6.10" >> ~/.bashrc \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["/bin/bash"]
