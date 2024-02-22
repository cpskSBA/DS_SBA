FROM python:3.8

COPY ./requirements.txt .

#Install python packages
RUN pip install --no-cache-dir -r ./requirements.txt

# # set an 
# ARG env_prefix=sbdh

# # Copy the shell script to the image
# COPY detect_os.sh /tmp/detect_os.sh

# # Run the shell script to detect the operating system and set environment variables accordingly
# RUN chmod +x /tmp/detect_os.sh && /tmp/detect_os.sh ${env_prefix}

# RUN rm /tmp/detect_os.sh

# # Read the environment variable file and set the variables
# RUN cat /tmp/env.list | while read line; do export "$line"; done \
#     && rm /tmp/env.list

# # # Clean up the temporary file
# # RUN rm /tmp/env.list

# Expose the port the app will be running from
EXPOSE 8501

# Create a separate app directory for the application files
RUN mkdir /app

# Set the application files as the default working directory
WORKDIR /app

#Copy scripts locally
COPY ./src .

# Copy docker entrypoint file
COPY ./docker/entrypoint.sh .

#set permissions on scripts so they can run
RUN chmod 555 Local_Scorecard.py SBA_DO_ZIP_matching_table.csv entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]