# start nameserver
# start file server
# TODO: start peers

echo "Starting nameserver and file server..."
echo ""

parallel -u ::: 'pyro5-ns' \
                './fileserver.py' \

echo ""
echo "Bye."
