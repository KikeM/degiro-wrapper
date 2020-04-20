docker build -t degiro:0.1.0 . \
&& docker run --name degiro \
           --volume $(pwd):$(pwd) \
            -it degiro:0.1.0
